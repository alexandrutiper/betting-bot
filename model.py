"""
MODEL MATEMATIC - CLEAN VERSION

✔ remove vig corect
✔ Poisson stabil
✔ piețe sigure
"""

import math


def remove_vig(odds):
    """
    Elimină marja bookmaker-ului.

    Transformă cote → probabilități reale.
    """

    inv = [1 / o for o in odds if o]

    total = sum(inv)

    return [p / total for p in inv]


def poisson(k, lam):
    return (lam ** k * math.exp(-lam)) / math.factorial(k)


def expected_goals(home_prob, away_prob):
    """
    Model simplu (baseline).

    IMPORTANT:
    aici vom integra forma echipelor în viitor.
    """

    total_goals = 2.6

    ratio = home_prob / away_prob if away_prob else 1

    lam_home = total_goals * ratio / (1 + ratio)
    lam_away = total_goals / (1 + ratio)

    return lam_home, lam_away


def poisson_probs(lh, la):

    home = draw = away = 0

    for i in range(7):
        for j in range(7):

            p = poisson(i, lh) * poisson(j, la)

            if i > j:
                home += p
            elif i == j:
                draw += p
            else:
                away += p

    return home, draw, away


def goal_distribution(lh, la):

    dist = {}

    for i in range(7):
        for j in range(7):

            p = poisson(i, lh) * poisson(j, la)
            total = i + j

            dist[total] = dist.get(total, 0) + p

    return dist


def double_chance(home, draw, away):
    return {
        "1X": home + draw,
        "X2": draw + away
    }


def goal_markets(dist):
    return {
        "over15": sum(v for k, v in dist.items() if k >= 2),
        "under45": sum(v for k, v in dist.items() if k <= 4)
    }
