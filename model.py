# model.py

# =====================================================
# MODEL MATEMATIC FOLOSIT DE BOT
# =====================================================
# acest fisier contine toate formulele statistice
# care decid ce pariuri sunt mai bune
#
# nou: League Confidence Factor
# =====================================================

import leagues


# =====================================================
# TRANSFORMARE COTA -> PROBABILITATE
# =====================================================
# bookmaker odds -> implied probability

def odds_to_probability(odd):

    if odd <= 0:
        return 0

    return 1 / odd


# =====================================================
# CAT DE CLAR ESTE FAVORITUL
# =====================================================
# daca diferenta dintre cote e mare
# meciul este mai "predictibil"

def market_strength(odds):

    ordered = sorted(odds)

    best = ordered[0]
    second = ordered[1]

    # exemplu:
    # 1.40 vs 4.50 -> strength mare
    # 2.40 vs 2.60 -> strength mic

    return second / best


# =====================================================
# ELIMINAREA MARJEI BOOKMAKERULUI
# =====================================================
# normalizeaza probabilitatile

def normalize_probabilities(odds):

    inv = [1 / o for o in odds]

    total = sum(inv)

    normalized = [p / total for p in inv]

    return normalized


# =====================================================
# DOUBLE CHANCE
# =====================================================

def double_chance(prob_home, prob_draw, prob_away):

    return {

        "1X": prob_home + prob_draw,
        "X2": prob_draw + prob_away,
        "12": prob_home + prob_away
    }


# =====================================================
# DRAW NO BET
# =====================================================

def draw_no_bet(prob_home, prob_draw, prob_away):

    # protecție divizare

    if prob_draw >= 0.99:
        return {}

    home = prob_home / (1 - prob_draw)
    away = prob_away / (1 - prob_draw)

    return {

        "home_dnb": home,
        "away_dnb": away
    }


# =====================================================
# LEAGUE FACTOR
# =====================================================
# adaugam incredere diferita pentru ligi

def league_factor(league):

    priority = leagues.LEAGUE_PRIORITY.get(league, 1)

    # conversie prioritate -> multiplicator

    if priority == 3:
        return 1.15

    if priority == 2:
        return 1.05

    return 0.95


# =====================================================
# PENALTY PENTRU LIGI VOLATILE
# =====================================================
# unele ligi au varianta mare de rezultate

VOLATILE_LEAGUES = {

    "soccer_usa_mls",
    "soccer_australia_aleague",
    "soccer_colombia_primera_a",
    "soccer_chile_primera_division"
}


def volatility_penalty(league):

    if league in VOLATILE_LEAGUES:
        return 0.9

    return 1.0


# =====================================================
# SCOR FINAL PARIU
# =====================================================
# aceasta este formula principala a botului

def pick_score(prob, strength, consensus, league=None):

    base_score = prob * strength / (1 + consensus)

    if league:

        # boost ligi bune
        base_score *= league_factor(league)

        # penalizare ligi haotice
        base_score *= volatility_penalty(league)

    return base_score