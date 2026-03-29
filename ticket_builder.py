"""
TICKET BUILDER - BILET COTA ~2 (FINAL VERSION)

───────────────────────────────────────────────────────
🎯 SCOP
───────────────────────────────────────────────────────

Construiește automat un bilet combinat stabil:

✔ cotă target: ~2 (configurabil)
✔ probabilitate maximă (optimizare)
✔ selecții sigure (low volatility)

───────────────────────────────────────────────────────
🧠 LOGICĂ GENERALĂ
───────────────────────────────────────────────────────

1. filtrăm selecțiile candidate (pool)
2. generăm combinații (combinatorică controlată)
3. filtrăm după cotă totală
4. rulăm Monte Carlo
5. alegem combinația cu probabilitate maximă

───────────────────────────────────────────────────────
⚠️ BUG FIX CRITIC
───────────────────────────────────────────────────────

Anterior:
❌ returna "bets"

Acum:
✔ returnează "selections"

→ standard unificat cu main.py
"""

import random
import math
import config
from itertools import combinations


# ======================================================
# FILTRARE MARKETURI PERMISE
# ======================================================

def allowed_market(bet):
    """
    Permitem DOAR piețe stabile.

    MOTIV:
    - vrem volatilitate mică
    - evităm pariuri riscante

    PERMISE:
    ✔ 1X
    ✔ X2
    ✔ over15

    ELIMINATE:
    ❌ under45 (deja prea multe în daily)
    ❌ DNB (ai decis să-l scoți)
    """

    return bet in {"1X", "X2", "over15"}


# ======================================================
# SIMULARE MONTE CARLO
# ======================================================

def simulate_ticket(selections):
    """
    Simulează probabilitatea biletului.

    LOGICĂ:
    - fiecare selecție are probabilitate "prob"
    - biletul câștigă doar dacă toate câștigă

    SIMULĂRI:
    - config.SIMULATIONS (ex: 50k)
    """

    wins = 0

    for _ in range(config.SIMULATIONS):

        success = True

        for bet in selections:

            # random() → [0,1]
            if random.random() > bet["prob"]:
                success = False
                break

        if success:
            wins += 1

    return wins / config.SIMULATIONS


# ======================================================
# BUILD TICKET (FUNCȚIA PRINCIPALĂ)
# ======================================================

def build_ticket(pool):
    """
    Construiește biletul optim.

    INPUT:
    - pool = lista de daily picks

    OUTPUT:
    - dict ticket SAU None

    STRUCTURĂ OUTPUT:
    {
        "odds": float,
        "prob": float,
        "selections": [...]
    }
    """

    # ==================================================
    # 1. FILTRARE POOL
    # ==================================================

    pool = [
        p for p in pool
        if p["odds"] <= config.MAX_SELECTION_ODDS
        and allowed_market(p["bet"])
    ]

    # dacă nu avem suficiente selecții → stop
    if len(pool) < config.MIN_MATCHES_PER_TICKET:
        return None

    best_ticket = None
    best_prob = 0

    # ==================================================
    # 2. GENERARE COMBINAȚII
    # ==================================================

    for size in range(
        config.MIN_MATCHES_PER_TICKET,
        config.MAX_MATCHES_PER_TICKET + 1
    ):

        for combo in combinations(pool, size):

            # evităm duplicate (același meci)
            matches = {c["match"] for c in combo}
            if len(matches) != len(combo):
                continue

            # ==================================================
            # 3. CALCUL COTĂ
            # ==================================================

            odds = math.prod(c["odds"] for c in combo)

            if not (
                config.MIN_TOTAL_ODDS <= odds <= config.MAX_TOTAL_ODDS
            ):
                continue

            # ==================================================
            # 4. MONTE CARLO
            # ==================================================

            prob = simulate_ticket(combo)

            # ==================================================
            # 5. BEST SELECTION
            # ==================================================

            if prob > best_prob:
                best_prob = prob
                best_ticket = combo

    if not best_ticket:
        return None

    # ==================================================
    # 6. OUTPUT FINAL (STANDARDIZAT)
    # ==================================================

    return {
        "odds": round(math.prod(c["odds"] for c in best_ticket), 2),
        "prob": best_prob,
        "selections": list(best_ticket)
    }
