# ticket_builder.py

"""
Acest fișier conține OPTIMIZERUL PROFESIONAL al aplicației.

Rolul său:
- Primește lista de pickuri candidate
- Generează sute de portofolii posibile
- Rulează simulări Monte Carlo
- Optimizează după:
    - Probabilitate ≥1 bilet câștigător
    - Profit așteptat
    - Stabilitate (probabilitate zi negativă)
    - Penalizare corelație (overlap)
"""

import random
import math
import config
from itertools import combinations


# ==========================================================
# Grupare pickuri pe meci
# ==========================================================

def group_by_match(picks):
    """
    Grupăm toate variantele disponibile pentru fiecare meci.
    Scop:
        - evităm să tratăm fiecare pick separat
        - controlăm corelația
    """

    matches = {}

    for p in picks:
        matches.setdefault(p["match"], []).append(p)

    grouped = []

    for match, variants in matches.items():

        # sortăm variantele după scor (cea mai bună prima)
        variants = sorted(variants, key=lambda x: x["score"], reverse=True)

        grouped.append({
            "match": match,
            "variants": variants[:3]  # max 3 variante per meci
        })

    return grouped


# ==========================================================
# Construire bilet
# ==========================================================

def build_ticket(bets):
    """
    Primește o listă de pariuri și calculează cota totală.
    """

    odds = math.prod(b["odds"] for b in bets)

    return {
        "bets": bets,
        "odds": round(odds, 2),
        "stake": config.STAKE
    }


# ==========================================================
# Motor Monte Carlo
# ==========================================================

def simulate_portfolio(tickets):
    """
    Simulează o zi de meciuri de config.SIMULATIONS ori.
    Important:
        - fiecare meci este simulat o singură dată per rundă
        - biletele folosesc aceleași rezultate (corelație reală)
    """

    success = 0
    total_profit = 0
    loss_days = 0

    for _ in range(config.SIMULATIONS):

        results = {}

        # Simulăm fiecare meci o singură dată
        for t in tickets:
            for b in t["bets"]:
                if b["match"] not in results:
                    results[b["match"]] = random.random() < b["prob"]

        daily_profit = -config.STAKE * len(tickets)
        won_any = False

        # Verificăm fiecare bilet
        for t in tickets:

            if all(results[b["match"]] for b in t["bets"]):
                won_any = True
                daily_profit += config.STAKE * t["odds"]

        if won_any:
            success += 1

        if daily_profit < 0:
            loss_days += 1

        total_profit += daily_profit

    return {
        "prob_at_least_one": success / config.SIMULATIONS,
        "expected_profit": total_profit / config.SIMULATIONS,
        "loss_probability": loss_days / config.SIMULATIONS
    }


# ==========================================================
# Penalizare overlap
# ==========================================================

def overlap_penalty(tickets):
    """
    Penalizează dacă biletele au prea multe meciuri comune.
    """
    penalty = 0

    for t1, t2 in combinations(tickets, 2):
        m1 = {b["match"] for b in t1["bets"]}
        m2 = {b["match"] for b in t2["bets"]}
        penalty += len(m1 & m2)

    return penalty


# ==========================================================
# OPTIMIZER PRINCIPAL
# ==========================================================

def build_tickets(picks):

    if not picks:
        return [], "Nu există pickuri valide astăzi."

    match_pool = group_by_match(picks)

    best_portfolio = None
    best_score = -999
    best_metrics = None
    tested = 0

    # Testăm diferite structuri de bilete
    for matches_per_ticket in range(
        config.MIN_MATCHES_PER_TICKET,
        config.MAX_MATCHES_PER_TICKET + 1
    ):

        for _ in range(600):

            if len(match_pool) < matches_per_ticket:
                continue

            tickets = []

            for _ in range(config.TICKETS_PER_DAY):

                selected = random.sample(match_pool, matches_per_ticket)
                bets = [random.choice(m["variants"]) for m in selected]

                ticket = build_ticket(bets)

                # Validare cotă totală
                if not (config.MIN_TOTAL_ODDS <= ticket["odds"] <= config.MAX_TOTAL_ODDS):
                    break

                tickets.append(ticket)

            if len(tickets) != config.TICKETS_PER_DAY:
                continue

            metrics = simulate_portfolio(tickets)

            if metrics["prob_at_least_one"] < config.MIN_PORTFOLIO_WIN_CHANCE:
                continue

            penalty = overlap_penalty(tickets)

            # Scor multi-obiectiv
            score = (
                0.6 * metrics["prob_at_least_one"] +
                0.3 * max(0, metrics["expected_profit"] / 100) +
                0.1 * (1 - metrics["loss_probability"])
            ) - 0.01 * penalty

            tested += 1

            if score > best_score:
                best_score = score
                best_portfolio = tickets
                best_metrics = metrics

    if not best_portfolio:
        return [], "Nu există portofoliu matematic valid astăzi."

    summary = (
        f"🧠 PROFESSIONAL OPTIMIZER\n"
        f"Portofolii testate: {tested}\n"
        f"Simulări per portofoliu: {config.SIMULATIONS}\n"
        f"Șansă ≥1 bilet câștigător: {round(best_metrics['prob_at_least_one']*100,2)}%\n"
        f"Profit mediu estimat: {round(best_metrics['expected_profit'],2)} lei\n"
        f"Probabilitate zi negativă: {round(best_metrics['loss_probability']*100,2)}%\n"
    )

    return best_portfolio, summary