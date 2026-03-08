"""
ENGINE PRINCIPAL BOT BETTING

Acest fișier este "creierul" aplicației.

Fluxul complet al botului:

1️⃣ preia meciurile din Odds API
2️⃣ filtrează meciurile din următoarele 12 ore
3️⃣ generează DAILY PICKS
4️⃣ construiește pool-ul pentru optimizer
5️⃣ rulează optimizerul pentru bilet cotă 2
6️⃣ trimite rezultatele pe Telegram
"""

from datetime import datetime, timezone, timedelta

import scraper
import model
import config
import telegram_bot
import ticket_builder
import market_converter


# ==========================================================
# 1️⃣ FETCH MATCHES
# ==========================================================

matches = scraper.get_matches()

print("====================================================")
print("Total meciuri primite din API:", len(matches))


# ==========================================================
# 2️⃣ FILTRARE MECIURI ÎN URMĂTOARELE 12 ORE
# ==========================================================

now = datetime.now(timezone.utc)
limit = now + timedelta(hours=config.MATCH_WINDOW_HOURS)

filtered_matches = []

eliminated_started = 0
eliminated_future = 0

for match in matches:

    kickoff = datetime.fromisoformat(
        match["commence_time"].replace("Z", "+00:00")
    )

    if kickoff <= now:
        eliminated_started += 1
        continue

    if kickoff > limit:
        eliminated_future += 1
        continue

    filtered_matches.append(match)

matches = filtered_matches

print("Meciuri în următoarele 12 ore:", len(matches))
print("Eliminate (deja începute):", eliminated_started)
print("Eliminate (prea departe):", eliminated_future)
print("====================================================")


# ==========================================================
# 3️⃣ DAILY PICKS
# ==========================================================

daily_candidates = []

for match in matches:

    odds_values = list(match["odds"].values())

    if len(odds_values) != 3:
        continue

    probs = model.normalize_probabilities(odds_values)

    strength = model.market_strength(odds_values)

    dc = model.double_chance(*probs)

    for bet, prob in dc.items():

        if prob < config.DAILY_MIN_PROB:
            continue

        odd = round(1 / prob, 2)

        if odd < 1.15:
            continue

        daily_candidates.append({

            "match": f"{match['home']} vs {match['away']}",
            "bet": bet,
            "prob": prob,
            "odds": odd,
            "strength": strength,
            "league": match["league"]

        })


daily_candidates = sorted(
    daily_candidates,
    key=lambda x: x["prob"],
    reverse=True
)

daily_candidates = daily_candidates[:config.DAILY_PICKS]


# ==========================================================
# TRIMITERE DAILY PICKS TELEGRAM
# ==========================================================

msg = "🔥 DAILY PICKS\n"
msg += "━━━━━━━━━━━━━━━\n\n"

if not daily_candidates:

    msg += "Nu există daily picks valide în interval.\n"

else:

    for pick in daily_candidates:

        market = market_converter.convert_market(pick["bet"])

        explanation = model.pick_explanation(
            pick["prob"],
            pick["strength"],
            pick["league"]
        )

        msg += f"⚽ {pick['match']}\n"
        msg += f"➡️ {market} @{pick['odds']}\n"
        msg += f"{explanation}\n\n"

telegram_bot.send_message(msg)


# ==========================================================
# 4️⃣ CONSTRUIRE POOL PENTRU OPTIMIZER
# ==========================================================

pool = []

for match in matches:

    odds_values = list(match["odds"].values())

    if len(odds_values) != 3:
        continue

    probs = model.normalize_probabilities(odds_values)

    strength = model.market_strength(odds_values)

    if strength < config.MIN_MARKET_STRENGTH:
        continue

    dc = model.double_chance(*probs)

    dnb = model.draw_no_bet(*probs)

    markets = {**dc, **dnb}

    for bet, prob in markets.items():

        if prob < config.MIN_SELECTION_PROB:
            continue

        odd = 1 / prob

        score = model.pick_score(
            prob,
            strength,
            match["consensus"],
            match["league"]
        )

        pool.append({

            "match": f"{match['home']} vs {match['away']}",
            "league": match["league"],
            "bet": bet,
            "prob": prob,
            "odds": odd,
            "score": score,
            "strength": strength

        })


pool = sorted(pool, key=lambda x: x["score"], reverse=True)
pool = pool[:40]

print("Selection pool size:", len(pool))


# ==========================================================
# 5️⃣ OPTIMIZER BILET
# ==========================================================

ticket, summary = ticket_builder.build_ticket_from_pool(pool)

# dacă nu există bilet valid
if not ticket:

    msg = "⚠️ NU EXISTĂ BILET VALID\n"
    msg += "━━━━━━━━━━━━━━\n\n"

    msg += "Algoritmul nu a găsit o combinație\n"
    msg += "care să respecte criteriile de siguranță.\n\n"

    msg += "🔎 Motive posibile:\n"
    msg += "• prea puține meciuri în interval\n"
    msg += "• ligi foarte volatile\n"
    msg += "• cotele nu permit formarea unei cote 2\n\n"

    msg += "⏳ Botul va încerca din nou la următoarea rulare."

    telegram_bot.send_message(msg)

    print("Nu există bilet valid.")
    print("====================================================")

    exit()

telegram_bot.send_message(summary)


# ==========================================================
# 6️⃣ FORMATARE BILET FINAL
# ==========================================================

msg = "🎯 BILET COTA 2\n"
msg += "━━━━━━━━━━━━━━\n\n"

msg += f"Cota totală: {ticket['odds']}\n\n"

for bet in ticket["bets"]:

    market = market_converter.convert_market(bet["bet"])

    explanation = model.pick_explanation(
        bet["prob"],
        bet["strength"],
        bet["league"]
    )

    msg += f"⚽ {bet['match']}\n"
    msg += f"➡️ {market} @{round(bet['odds'],2)}\n"
    msg += f"{explanation}\n\n"


telegram_bot.send_message(msg)

print("Bot finalizat cu succes.")
print("====================================================")