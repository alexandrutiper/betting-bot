"""
OPTIMIZER BILET COTA 2

Algoritmul:

1. generează combinații de selecții
2. filtrează biletele după cotă
3. rulează simulări Monte Carlo
4. alege biletul cu probabilitatea maximă
"""

import random
import math
import config
from itertools import combinations


# ==========================================================
# CONSTRUIRE BILET
# ==========================================================

def build_ticket(bets):

    odds = math.prod(b["odds"] for b in bets)

    return {

        "bets": bets,
        "odds": round(odds,2)
    }


# ==========================================================
# MONTE CARLO
# ==========================================================

def simulate_ticket(ticket):

    wins = 0

    for _ in range(config.SIMULATIONS):

        success = True

        for bet in ticket["bets"]:

            if random.random() > bet["prob"]:
                success = False
                break

        if success:
            wins += 1

    return wins/config.SIMULATIONS


# ==========================================================
# FILTRARE PIEȚE
# ==========================================================

def allowed_market(bet):

    """
    Permitem doar piețele stabile.
    """

    allowed = {

        "1X",
        "X2",
        "home_dnb",
        "over15"
    }

    return bet in allowed


# ==========================================================
# OPTIMIZER
# ==========================================================

def build_ticket_from_pool(pool):

    best_ticket = None
    best_prob = 0

    # filtrăm selecțiile candidate

    pool = [

        p for p in pool
        if p["odds"] <= config.MAX_SELECTION_ODDS
        and allowed_market(p["bet"])
    ]

    for size in range(
        config.MIN_MATCHES_PER_TICKET,
        config.MAX_MATCHES_PER_TICKET+1
    ):

        combos = combinations(pool,size)

        for combo in combos:

            matches = {c["match"] for c in combo}

            if len(matches) != len(combo):
                continue

            ticket = build_ticket(combo)

            if not (
                config.MIN_TOTAL_ODDS
                <= ticket["odds"]
                <= config.MAX_TOTAL_ODDS
            ):
                continue

            prob = simulate_ticket(ticket)

            if prob > best_prob:

                best_prob = prob
                best_ticket = ticket

    if not best_ticket:
        return None, None

    summary = f"""
🧠 OPTIMIZER MATEMATIC

Simulări Monte Carlo: {config.SIMULATIONS}

Probabilitate câștig bilet:
{round(best_prob*100,2)}%

Cotă bilet:
{best_ticket['odds']}
"""

    return best_ticket,summary