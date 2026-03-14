
"""
OPTIMIZER RAPID PENTRU BILET COTA 2

Acest optimizer este mult mai eficient decât
versiunea brută care testa toate combinațiile.

Strategia folosită:

1️⃣ generăm toate combinațiile candidate
2️⃣ calculăm probabilitatea rapidă (multiplicare)
3️⃣ păstrăm doar cele mai bune bilete
4️⃣ rulăm Monte Carlo doar pentru finaliști

Avantaj:
- 10x – 50x mai rapid
"""

import random
import math
import config
from itertools import combinations


# ======================================================
# PROBABILITATE RAPIDĂ
# ======================================================

def fast_ticket_prob(ticket):
    """
    Aproximare rapidă a probabilității biletului.

    Deoarece evenimentele sunt aproximativ independente,
    putem aproxima probabilitatea totală prin
    produsul probabilităților individuale.
    """

    prob = 1

    for bet in ticket:
        prob *= bet["prob"]

    return prob


# ======================================================
# MONTE CARLO
# ======================================================

def simulate(ticket):
    """
    Simulează rezultatul biletului folosind
    Monte Carlo.

    Această funcție este costisitoare, deci
    o rulăm doar pentru finaliști.
    """

    wins = 0

    for _ in range(config.SIMULATIONS):

        success = True

        for bet in ticket:

            if random.random() > bet["prob"]:
                success = False
                break

        if success:
            wins += 1

    return wins / config.SIMULATIONS


# ======================================================
# CALCUL COTA BILET
# ======================================================

def ticket_odds(ticket):

    odds = 1

    for bet in ticket:
        odds *= bet["odds"]

    return odds


# ======================================================
# OPTIMIZER PRINCIPAL
# ======================================================

def build_ticket(pool):

    """
    Construiește biletul optim.

    Flux:
    1️⃣ generăm bilete candidate
    2️⃣ filtrăm după cotă
    3️⃣ sortăm după probabilitate rapidă
    4️⃣ Monte Carlo pentru finaliști
    """

    if len(pool) < config.MIN_MATCHES_PER_TICKET:
        return None

    candidates = []

    # ==================================================
    # GENERARE COMBINAȚII
    # ==================================================

    for size in range(
        config.MIN_MATCHES_PER_TICKET,
        config.MAX_MATCHES_PER_TICKET + 1
    ):

        for combo in combinations(pool, size):

            odds = ticket_odds(combo)

            if odds < config.MIN_TOTAL_ODDS:
                continue

            if odds > config.MAX_TOTAL_ODDS:
                continue

            prob = fast_ticket_prob(combo)

            candidates.append((combo, prob))

    if not candidates:
        return None

    # ==================================================
    # SELECTĂM CELE MAI BUNE CANDIDATE
    # ==================================================

    candidates = sorted(
        candidates,
        key=lambda x: x[1],
        reverse=True
    )

    finalists = candidates[:config.FINAL_TICKET_CANDIDATES]

    # ==================================================
    # MONTE CARLO FINAL
    # ==================================================

    best_ticket = None
    best_prob = 0

    for ticket, _ in finalists:

        prob = simulate(ticket)

        if prob > best_prob:

            best_prob = prob
            best_ticket = ticket

    return best_ticket