"""
MODEL MATEMATIC

Acest modul conține toate formulele matematice
folosite pentru evaluarea pariurilor.

Modele implementate:

• normalizare probabilități
• market strength
• league reliability
• volatility penalty
• Poisson goals model
"""

import leagues
import math


# ==========================================================
# NORMALIZARE PROBABILITĂȚI
# ==========================================================

def normalize_probabilities(odds):

    inv = [1/o for o in odds]

    total = sum(inv)

    return [p/total for p in inv]


# ==========================================================
# MARKET STRENGTH
# ==========================================================

def market_strength(odds):

    ordered = sorted(odds)

    best = ordered[0]
    second = ordered[1]

    return second / best


# ==========================================================
# DOUBLE CHANCE
# ==========================================================

def double_chance(home,draw,away):

    return {

        "1X": home + draw,
        "X2": draw + away
    }


# ==========================================================
# DRAW NO BET
# ==========================================================

def draw_no_bet(home,draw,away):

    if draw >= 0.99:
        return {}

    home_dnb = home/(1-draw)

    return {

        "home_dnb": home_dnb
    }


# ==========================================================
# POISSON MODEL
# ==========================================================

def poisson_prob(lmbda,k):

    return (lmbda**k * math.exp(-lmbda)) / math.factorial(k)


def over15_probability(home_attack,away_attack):

    lam = home_attack + away_attack

    p0 = poisson_prob(lam,0)
    p1 = poisson_prob(lam,1)

    return 1 - (p0+p1)


# ==========================================================
# LEAGUE FACTOR
# ==========================================================

def league_factor(league):

    priority = leagues.LEAGUE_PRIORITY.get(league,1)

    if priority == 3:
        return 1.15

    if priority == 2:
        return 1.05

    return 0.9


# ==========================================================
# VOLATILITY PENALTY
# ==========================================================

VOLATILE = {

    "soccer_usa_mls",
    "soccer_australia_aleague",
    "soccer_chile_primera_division",
    "soccer_mexico_ligamx"
}

def volatility_penalty(league):

    if league in VOLATILE:
        return 0.80

    return 1.0


# ==========================================================
# SCOR FINAL PICK
# ==========================================================

def pick_score(prob,strength,consensus,league):

    score = prob * strength / (1+consensus)

    score *= league_factor(league)

    score *= volatility_penalty(league)

    return score

# ==========================================================
# EXPLICAȚIE PICK
# ==========================================================

def pick_explanation(prob, strength, league):

    """
    Generează o explicație foarte scurtă
    pentru selecția făcută de algoritm.

    Aceasta este trimisă pe Telegram
    pentru a înțelege de ce a fost ales pariul.
    """

    prob_percent = round(prob * 100)

    if strength > 1.5:
        fav = "Fav puternic"
    elif strength > 1.3:
        fav = "Fav clar"
    else:
        fav = "Fav moderat"

    if league_factor(league) > 1.1:
        league_label = "Liga stabilă"
    elif league_factor(league) > 1.0:
        league_label = "Liga ok"
    else:
        league_label = "Liga volatilă"

    return f"📊 Prob: {prob_percent}% | {fav} | {league_label}"