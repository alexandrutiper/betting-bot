"""
JOKER1X - MAIN ENGINE (FINAL ULTRA COMMENTED VERSION)

───────────────────────────────────────────────────────
🎯 SCOPUL ACESTUI FIȘIER
───────────────────────────────────────────────────────

Acest fișier este "creierul" botului.

El coordonează TOT fluxul:

1. Inițializare DB
2. Update rezultate (bankroll)
3. Generare selecții (model matematic)
4. Filtrare + scoring
5. Salvare în DB
6. Construire mesaje Telegram (UX)
7. Trimitere mesaje separate (IMPORTANT)

───────────────────────────────────────────────────────
⚠️ FOARTE IMPORTANT
───────────────────────────────────────────────────────

✔ NU am modificat algoritmul tău
✔ NU am schimbat logica matematică
✔ NU am afectat performanța

👉 Am modificat DOAR:
- UX mesaje
- structură output
- claritate cod

───────────────────────────────────────────────────────
📦 STRUCTURĂ MESAJE TELEGRAM
───────────────────────────────────────────────────────

1️⃣ Greeting (Bună dimineața / seara)
2️⃣ DAILY PICKS
3️⃣ BILET COTA 2
4️⃣ Closing (O zi bună / Noapte bună)

👉 fiecare trimis SEPARAT (fără duplicări)
"""

from datetime import datetime, timezone, timedelta

# module interne
import scraper
import model
import telegram_bot
import config
import db


# ======================================================
# LOGGING HELPER
# ======================================================

def log(x):
    """
    Helper simplu pentru debug/logging.

    flush=True → important pentru Railway (loguri live)
    """
    print(f"[JOKER1X] {x}", flush=True)


# ======================================================
# GREETING + CLOSING (UX CRITICAL)
# ======================================================

def get_greeting():
    """
    Returnează mesaj de început în funcție de oră.

    IMPORTANT UX:
    - NU folosim "noapte bună" la început
    - greeting trebuie să fie natural
    """

    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "🌅 Bună dimineața!"
    elif 12 <= hour < 18:
        return "☀️ Bună ziua!"
    else:
        return "🌙 Bună seara!"


def get_closing():
    """
    Mesaj final (închidere conversație).

    IMPORTANT:
    - dimineața → "o zi bună"
    - seara → "noapte bună"
    """

    hour = datetime.now().hour

    if 5 <= hour < 18:
        return "💚 O zi bună și pariuri inspirate!"
    else:
        return "🌙 Noapte bună și mult succes!"


# ======================================================
# STAKE MODEL (NEMODIFICAT)
# ======================================================

def compute_stake(prob, edge, bet_type, roi_data):
    """
    Calculează stake-ul pentru fiecare pariu.

    FACTORI:
    ✔ probabilitate (încredere)
    ✔ edge (valoare reală)
    ✔ ROI (auto-learning din DB)

    DESIGN:
    - stabil (nu Kelly full → prea volatil)
    - limitat între 2 și 10 lei
    """

    MIN_PROB = 0.78
    MAX_PROB = 0.90

    # -------------------------------
    # NORMALIZARE PROBABILITATE
    # -------------------------------

    if prob <= MIN_PROB:
        conf = 0
    elif prob >= MAX_PROB:
        conf = 1
    else:
        conf = (prob - MIN_PROB) / (MAX_PROB - MIN_PROB)

    # -------------------------------
    # EDGE (VALUE)
    # -------------------------------

    edge_factor = min(max(edge, 0) * 10, 1)

    # -------------------------------
    # ROI (AUTO LEARNING)
    # -------------------------------

    roi = roi_data.get(bet_type, 0)
    roi_factor = max(-0.2, min(roi, 0.2))

    # -------------------------------
    # SCORE FINAL
    # -------------------------------

    score = (
        0.6 * conf +
        0.3 * edge_factor +
        0.1 * (roi_factor + 0.2)
    )

    # stake între 2 și 10 lei
    return round(2 + score * 8, 2)


# ======================================================
# MAIN FUNCTION
# ======================================================

def main():

    log("START")

    # ==================================================
    # 1. INIT DB + UPDATE REZULTATE
    # ==================================================

    db.init_db()

    # update rezultate (meciuri finalizate)
    # → actualizează profit + bankroll
    db.check_results(scraper)

    # ==================================================
    # 2. AUTO-LEARNING (ROI)
    # ==================================================

    roi_data = db.get_market_roi()

    # ==================================================
    # 3. FETCH MATCHES
    # ==================================================

    matches = scraper.get_matches()

    now = datetime.now(timezone.utc)
    limit = now + timedelta(hours=config.MATCH_WINDOW_HOURS)

    daily = []              # lista finală de picks
    under45_count = 0      # limitare spam under45

    # ==================================================
    # 4. GENERARE SELECȚII (MODELUL TĂU ORIGINAL)
    # ==================================================

    for m in matches:

        # parsare timp meci
        try:
            kickoff = datetime.fromisoformat(
                m["commence_time"].replace("Z", "+00:00")
            )
        except:
            continue

        # filtrăm doar meciuri relevante (ex: următoarele 12h)
        if not (now < kickoff <= limit):
            continue

        # --------------------------------------------
        # 1. REMOVE VIG (probabilități reale)
        # --------------------------------------------

        probs = model.remove_vig(list(m["odds"].values()))
        home, draw, away = probs

        # --------------------------------------------
        # 2. POISSON MODEL
        # --------------------------------------------

        lam_home, lam_away = model.expected_goals(home, away)

        home, draw, away = model.poisson_probs(lam_home, lam_away)
        dist = model.goal_distribution(lam_home, lam_away)

        # --------------------------------------------
        # 3. PIEȚE DERIVATE
        # --------------------------------------------

        markets = {}
        markets.update(model.double_chance(home, draw, away))
        markets.update(model.goal_markets(dist))

        # --------------------------------------------
        # 4. EVALUARE FIECARE PARIU
        # --------------------------------------------

        for bet, prob in markets.items():

            # mapare odds reale (CRITICAL pentru EDGE)
            real_odds_map = {
                "1X": 1 / (probs[0] + probs[1]),
                "X2": 1 / (probs[1] + probs[2]),
                "over15": m["goals"].get("over15"),
                "under45": 1 / prob  # fallback
            }

            real_odd = real_odds_map.get(bet)

            if not real_odd:
                continue

            # EDGE REAL (value betting)
            edge = prob - (1 / real_odd)

            if edge <= 0:
                continue

            # control spam under45
            if bet == "under45":
                if prob < 0.87 or under45_count >= 2:
                    continue
                under45_count += 1

            # stake calculat
            stake = compute_stake(prob, edge, bet, roi_data)

            # scoring pentru diversitate
            priority = {
                "1X": 1.0,
                "X2": 1.0,
                "over15": 0.9,
                "under45": 0.7
            }

            daily.append({
                "match": f"{m['home']} vs {m['away']}",
                "bet": bet,
                "prob": prob,
                "odds": real_odd,
                "edge": edge,
                "stake": stake,
                "score": prob * priority.get(bet, 0.5)
            })

    # ==================================================
    # 5. POST-PROCESARE
    # ==================================================

    # eliminăm duplicate (un singur pick per meci)
    daily = list({d["match"]: d for d in daily}.values())

    # sortare după scor
    daily = sorted(daily, key=lambda x: x["score"], reverse=True)

    # limităm numărul de picks
    daily = daily[:config.DAILY_PICKS]

    # salvăm în DB
    db.save_daily_picks(daily)

    # ==================================================
    # 6. TELEGRAM OUTPUT (PRO UX FLOW)
    # ==================================================

    greeting = get_greeting()
    closing = get_closing()

    bankroll = db.get_bankroll()
    total_stake = sum(d["stake"] for d in daily)
    risk_pct = (total_stake / bankroll * 100) if bankroll else 0

    # --------------------------------------------------
    # 1️⃣ GREETING
    # --------------------------------------------------

    telegram_bot.send_message(
        f"{greeting}\n\n🤖 Joker1X a analizat meciurile rămase ⚽"
    )

    # --------------------------------------------------
    # 2️⃣ DAILY PICKS
    # --------------------------------------------------

    if not daily:

        telegram_bot.send_message(
            "🔥 DAILY PICKS\n\n"
            "😴 Nicio selecție sigură azi.\n\n"
            "📉 Piața nu oferă value.\n"
            "⏳ Așteptăm oportunități mai bune.\n\n"
            "💡 Disciplina bate impulsul."
        )

    else:

        msg = "🔥 DAILY PICKS\n\n"

        msg += (
            f"💰 Bankroll: {round(bankroll,2)} lei\n"
            f"💸 Stake total: {round(total_stake,2)} lei\n"
            f"⚠️ Risc: {round(risk_pct,2)}%\n\n"
        )

        for d in daily:
            msg += (
                f"⚽ {d['match']}\n"
                f"➡️ {'Over 1.5 goals' if d['bet']=='over15' else 'Under 4.5 goals' if d['bet']=='under45' else d['bet']} | {round(d['odds'],2)} 🎯\n"
                f"📊 {round(d['prob']*100)}% | Edge {round(d['edge']*100,2)}%\n"
                f"💵 Stake: {d['stake']} lei\n\n"
            )

        telegram_bot.send_message(msg)

# ... TOT CODUL TĂU ESTE IDENTIC PÂNĂ LA BILET ...

    # --------------------------------------------------
    # 3️⃣ BILET COTA 2
    # --------------------------------------------------

    try:
        from ticket_builder import build_ticket
        ticket = build_ticket(daily)
    except:
        ticket = None

    if not ticket or not isinstance(ticket, dict) or "selections" not in ticket:

        telegram_bot.send_message(
            "🎯 BILET COTA 2\n\n"
            "❌ Nu există combinații stabile.\n"
            "📉 Nu forțăm pariurile.\n"
            "💡 Calitatea > cantitatea."
        )

    else:

        msg = "🎯 BILET COTA 2\n\n"

        msg += f"💰 Cotă totală: {round(ticket.get('odds', 0), 2)}\n\n"

        for t in ticket["selections"]:
            msg += f"• {t.get('match','?')} → {'Over 1.5 goals' if t.get('bet')=='over15' else 'Under 4.5 goals' if t.get('bet')=='under45' else t.get('bet','?')}\n"

        msg += f"\n📊 Probabilitate: {round(ticket.get('prob', 0)*100)}%\n"

        telegram_bot.send_message(msg)

    # ==================================================
    # 🔥 FIX REAL: CLOSING MUTAT AICI (GLOBAL, NU ÎN ELSE)
    # ==================================================

    telegram_bot.send_message(closing)

    # --------------------------------------------------
    # TELEGRAM COMMANDS
    # --------------------------------------------------

    telegram_bot.handle_commands()

    log("DONE")


if __name__ == "__main__":
    main()
