# ticket_checker.py

"""
Verifică biletele generate ieri,
calculează profit/pierdere,
actualizează bankroll,
marchează ziua ca verificată.
"""

import storage
import scraper
import config
from datetime import datetime, timedelta


def check_old_tickets():

    tickets_data = storage.get_tickets()
    bankroll_data = storage.get_bankroll()

    current_bankroll = bankroll_data["bankroll"]

    if not tickets_data:
        return None

    yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()

    for index, entry in enumerate(tickets_data):

        if entry["date"] != yesterday:
            continue

        if entry.get("checked"):
            return None

        results = scraper.get_scores()

        total_stake = config.STAKE * config.TICKETS_PER_DAY
        total_profit = -total_stake
        wins = 0

        message = f"📊 YESTERDAY RESULTS\n"
        message += f"📅 {yesterday}\n\n"

        for i, ticket in enumerate(entry["tickets"], 1):

            win = True

            for bet in ticket["bets"]:

                match = bet["match"]

                if match not in results:
                    win = False
                    break

                home = results[match]["home"]
                away = results[match]["away"]

                bet_type = bet["bet"]

                if bet_type == "1X" and home < away:
                    win = False
                elif bet_type == "X2" and away < home:
                    win = False
                elif bet_type == "1" and home <= away:
                    win = False
                elif bet_type == "2" and away <= home:
                    win = False

            message += f"🎫 Ticket {i}\n"

            if win:
                wins += 1
                payout = ticket["stake"] * ticket["odds"]
                total_profit += payout
                message += f"🟢 WON | Payout: {round(payout,2)} lei\n\n"
            else:
                message += f"🔴 LOST | -{ticket['stake']} lei\n\n"

        # Actualizăm bankroll
        new_bankroll = storage.update_bankroll(total_profit)
        storage.mark_checked(index, total_profit)

        roi = ((new_bankroll - config.START_BANKROLL) / config.START_BANKROLL) * 100

        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"💸 Total stake: {total_stake} lei\n"
        message += f"📈 Net Profit: {round(total_profit,2)} lei\n\n"
        message += f"💰 Bankroll înainte: {round(current_bankroll,2)} lei\n"
        message += f"💰 Bankroll acum: {round(new_bankroll,2)} lei\n"
        message += f"📊 ROI total: {round(roi,2)}%\n"

        return message

    return None