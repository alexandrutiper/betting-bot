"""
Joker1X MAIN ENGINE

Acest fișier este orchestratorul principal al botului.

Fluxul complet:

1️⃣ Preluăm meciurile din Odds API
2️⃣ Filtrăm meciurile care încep în următoarele X ore
3️⃣ Calculăm probabilitățile folosind modelul matematic
4️⃣ Construim pool-ul de selecții candidate
5️⃣ Generăm Daily Picks
6️⃣ Construim biletul cotă ~2 folosind optimizerul
7️⃣ Construim mesajele Telegram
8️⃣ Trimitem mesajele
"""

from datetime import datetime, timezone, timedelta

import scraper
import model
import optimizer
import telegram_bot
import market_converter
import config


def main():

    # ======================================================
    # INTRO DINAMIC (DIMINEAȚĂ / SEARĂ)
    # ======================================================

    hour = datetime.now().hour

    if hour < 15:

        intro = (
            "☀️ Bună dimineața!\n\n"
            "🤖 Joker1X a analizat meciurile zilei și a identificat cele mai stabile oportunități.\n\n"
        )

    else:

        intro = (
            "🌙 Bună seara!\n\n"
            "🤖 Joker1X a analizat meciurile rămase ale zilei și propune următoarele selecții.\n\n"
        )

    # ======================================================
    # COLECTARE MECIURI DIN API
    # ======================================================

    matches = scraper.get_matches()

    print("Total meciuri primite din API:", len(matches))

    # ======================================================
    # FILTRARE MECIURI DUPĂ INTERVAL
    # ======================================================

    now = datetime.now(timezone.utc)
    limit = now + timedelta(hours=config.MATCH_WINDOW_HOURS)

    filtered = []

    for m in matches:

        try:

            kickoff = datetime.fromisoformat(
                m["commence_time"].replace("Z", "+00:00")
            )

        except:
            continue

        if kickoff <= now:
            continue

        if kickoff > limit:
            continue

        filtered.append(m)

    print("Meciuri în interval:", len(filtered))

    # ======================================================
    # GENERARE SELECȚII CANDIDATE
    # ======================================================

    pool = []
    daily = []

    for match in filtered:

        odds = list(match["odds"].values())

        if None in odds:
            continue

        probs = model.remove_vig(odds)

        home_prob = probs[0]
        draw_prob = probs[1]
        away_prob = probs[2]

        lam_home, lam_away = model.expected_goals(
            home_prob,
            away_prob
        )

        home, draw, away = model.poisson_probs(
            lam_home,
            lam_away
        )

        goal_dist = model.goal_distribution(
            lam_home,
            lam_away
        )

        markets = {}

        markets.update(model.double_chance(home, draw, away))
        markets.update(model.draw_no_bet(home, draw, away))
        markets.update(model.goal_ranges(goal_dist))

        for bet, prob in markets.items():

            if prob <= 0:
                continue

            odd = 1 / prob

            pick = {
                "match": f"{match['home']} vs {match['away']}",
                "bet": bet,
                "prob": prob,
                "odds": odd
            }

            if prob >= config.MIN_SELECTION_PROB:
                pool.append(pick)

            if (
                prob >= config.DAILY_MIN_PROB
                and odd >= config.MIN_DAILY_ODDS
            ):
                daily.append(pick)

    print("Pool înainte limitare:", len(pool))

    # ======================================================
    # LIMITARE POOL
    # ======================================================

    pool = sorted(
        pool,
        key=lambda x: x["prob"],
        reverse=True
    )[:config.POOL_LIMIT]

    print("Pool după limitare:", len(pool))

    # ======================================================
    # DAILY PICKS
    # ======================================================

    daily = sorted(
        daily,
        key=lambda x: x["prob"],
        reverse=True
    )[:config.DAILY_PICKS]

    # ======================================================
    # MESAJ DAILY PICKS
    # ======================================================

    msg_daily = intro

    msg_daily += "🔥 DAILY PICKS\n"
    msg_daily += "━━━━━━━━━━━━━━━━━━━━\n\n"

    msg_daily += f"⚽ Meciuri analizate: {len(filtered)}\n"
    msg_daily += f"🎯 Selecții candidate: {len(pool)}\n\n"

    for d in daily:

        implied = 1 / d["odds"]
        edge = d["prob"] - implied

        msg_daily += f"⚽ {d['match']}\n"
        msg_daily += f"➡️ {market_converter.convert(d['bet'])}\n"
        msg_daily += f"💰 Cotă: {round(d['odds'],2)}\n"
        msg_daily += f"📊 Prob: {round(d['prob']*100)}%\n"
        msg_daily += f"📈 Edge: {round(edge*100,1)}%\n\n"

    msg_daily += "━━━━━━━━━━━━━━━━━━━━\n"
    msg_daily += "🤖 Joker1X Betting Model\n"

    # ======================================================
    # CONSTRUIRE BILET COTA ~2
    # ======================================================

    msg_ticket = "🎯 BILETUL ZILEI – COTA ~2\n"
    msg_ticket += "━━━━━━━━━━━━━━━━━━━━\n\n"

    ticket = optimizer.build_ticket(pool)

    if ticket:

        total_odds = 1
        ticket_prob = 1

        for bet in ticket:
            total_odds *= bet["odds"]
            ticket_prob *= bet["prob"]

        msg_ticket += f"💰 Cotă totală: {round(total_odds,2)}\n"
        msg_ticket += f"📊 Probabilitate model: {round(ticket_prob*100)}%\n"
        msg_ticket += f"🎟️ Selecții: {len(ticket)}\n\n"

        for bet in ticket:

            implied = 1 / bet["odds"]
            edge = bet["prob"] - implied

            msg_ticket += f"⚽ {bet['match']}\n"
            msg_ticket += f"➡️ {market_converter.convert(bet['bet'])}\n"
            msg_ticket += f"💰 Cotă: {round(bet['odds'],2)}\n"
            msg_ticket += f"📊 Prob: {round(bet['prob']*100)}%\n"
            msg_ticket += f"📈 Edge: {round(edge*100,1)}%\n\n"

    else:

        msg_ticket += "⚠️ Nu există combinație stabilă pentru acest interval.\n\n"

    msg_ticket += "\n━━━━━━━━━━━━━━━━━━━━\n"
    msg_ticket += "🤖 Joker1X Betting Model\n"
    msg_ticket += f"🧠 Monte Carlo: {config.SIMULATIONS}\n"
    msg_ticket += "🍀 Mult succes!\n"

    # ======================================================
    # TRIMITERE TELEGRAM
    # ======================================================

    telegram_bot.send_message(msg_daily)
    telegram_bot.send_message(msg_ticket)

    print("Mesaje trimise către Telegram.")


if __name__ == "__main__":

    try:
        main()

    except Exception as e:

        import traceback

        print("===== JOKER1X ERROR =====")
        print(str(e))
        traceback.print_exc()
        print("==========================")
