"""
Joker1X MAIN ENGINE
VERSIUNE DEBUGGING COMPLET PENTRU RAILWAY

Acest fișier loghează fiecare etapă pentru a identifica
exact unde apare eroarea în producție.
"""

from datetime import datetime, timezone, timedelta
import traceback
import sys

import scraper
import model
import optimizer
import telegram_bot
import market_converter
import config


def log(step):
    """
    Funcție simplă pentru logging clar în Railway.
    """
    print(f"[JOKER1X] {step}", flush=True)


def main():

    log("START BOT")

    # ======================================================
    # INTRO
    # ======================================================

    hour = datetime.now().hour

    if hour < 15:
        intro = (
            "☀️ Bună dimineața!\n\n"
            "🤖 Joker1X a analizat meciurile zilei.\n\n"
        )
    else:
        intro = (
            "🌙 Bună seara!\n\n"
            "🤖 Joker1X a analizat meciurile rămase.\n\n"
        )

    log("INTRO GENERATED")

    # ======================================================
    # GET MATCHES
    # ======================================================

    log("REQUEST MATCHES FROM API")

    matches = scraper.get_matches()

    log(f"MATCHES RECEIVED: {len(matches)}")

    # ======================================================
    # FILTER MATCHES
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

    log(f"MATCHES IN WINDOW: {len(filtered)}")

    # ======================================================
    # GENERATE SELECTIONS
    # ======================================================

    pool = []
    daily = []

    log("START MODEL PROCESSING")

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

    log(f"POOL BEFORE LIMIT: {len(pool)}")

    # ======================================================
    # LIMIT POOL
    # ======================================================

    pool = sorted(
        pool,
        key=lambda x: x["prob"],
        reverse=True
    )[:config.POOL_LIMIT]

    log(f"POOL AFTER LIMIT: {len(pool)}")

    # ======================================================
    # DAILY PICKS
    # ======================================================

    daily = sorted(
        daily,
        key=lambda x: x["prob"],
        reverse=True
    )[:config.DAILY_PICKS]

    log(f"DAILY PICKS COUNT: {len(daily)}")

    # ======================================================
    # DAILY MESSAGE
    # ======================================================

    msg_daily = intro

    msg_daily += "🔥 DAILY PICKS\n"
    msg_daily += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for d in daily:

        msg_daily += f"⚽ {d['match']}\n"
        msg_daily += f"➡️ {market_converter.convert(d['bet'])}\n"
        msg_daily += f"💰 Cotă: {round(d['odds'],2)}\n"
        msg_daily += f"📊 Prob: {round(d['prob']*100)}%\n\n"

    log("DAILY MESSAGE GENERATED")

    # ======================================================
    # OPTIMIZER
    # ======================================================

    log("RUN OPTIMIZER")

    ticket = optimizer.build_ticket(pool)

    log(f"TICKET RESULT: {ticket}")

    # ======================================================
    # TICKET MESSAGE
    # ======================================================

    msg_ticket = "🎯 BILETUL ZILEI – COTA ~2\n"
    msg_ticket += "━━━━━━━━━━━━━━━━━━━━\n\n"

    if ticket:

        total_odds = 1

        for bet in ticket:
            total_odds *= bet["odds"]

        msg_ticket += f"💰 Cotă totală: {round(total_odds,2)}\n\n"

        for bet in ticket:

            msg_ticket += f"⚽ {bet['match']}\n"
            msg_ticket += f"➡️ {market_converter.convert(bet['bet'])}\n"
            msg_ticket += f"💰 Cotă: {round(bet['odds'],2)}\n\n"

    else:

        msg_ticket += "⚠️ Nu s-a găsit bilet stabil.\n"

    log("TICKET MESSAGE GENERATED")

    # ======================================================
    # TELEGRAM SEND
    # ======================================================

    log("SEND TELEGRAM DAILY")

    telegram_bot.send_message(msg_daily)

    log("SEND TELEGRAM TICKET")

    telegram_bot.send_message(msg_ticket)

    log("MESSAGES SENT SUCCESSFULLY")


if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        print("\n===== JOKER1X CRASH =====\n")

        print("ERROR:", str(e))

        traceback.print_exc()

        print("\n=========================\n")

        sys.exit(0)
