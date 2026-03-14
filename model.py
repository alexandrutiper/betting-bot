
"""
MODEL MATEMATIC

Acest modul implementează:

1 eliminarea marjei bookmaker
2 estimarea golurilor așteptate
3 distribuția Poisson
4 probabilități pentru piețe
"""

import math


def remove_vig(odds):

    inv=[1/o for o in odds]

    total=sum(inv)

    return [p/total for p in inv]


def poisson(k,lam):

    return (lam**k*math.exp(-lam))/math.factorial(k)


def expected_goals(home_prob,away_prob):

    total_goals=2.6

    ratio=home_prob/away_prob if away_prob else 1

    lam_home=total_goals*ratio/(1+ratio)
    lam_away=total_goals/(1+ratio)

    return lam_home,lam_away


def goal_distribution(lam_home,lam_away):

    dist={}

    for i in range(7):
        for j in range(7):

            p=poisson(i,lam_home)*poisson(j,lam_away)

            total=i+j

            dist[total]=dist.get(total,0)+p

    return dist


def double_chance(home,draw,away):

    return{

        "1X":home+draw,
        "X2":draw+away
    }


def draw_no_bet(home,draw,away):

    if draw>0.95:
        return {}

    return{

        "home_dnb":home/(1-draw),
        "away_dnb":away/(1-draw)
    }


def goal_ranges(dist):

    return{

        "goals_1_4":dist.get(1,0)+dist.get(2,0)+dist.get(3,0)+dist.get(4,0),

        "goals_2_6":dist.get(2,0)+dist.get(3,0)+dist.get(4,0)+dist.get(5,0)+dist.get(6,0)
    }

def poisson_probs(lam_home, lam_away):
    """
    Calculează probabilitățile pentru:
    - victorie gazde
    - egal
    - victorie oaspeți

    folosind distribuția Poisson pentru golurile
    marcate de fiecare echipă.
    """

    home = 0
    draw = 0
    away = 0

    # iterăm scoruri posibile 0-0 până la 6-6
    for i in range(7):
        for j in range(7):

            p = poisson(i, lam_home) * poisson(j, lam_away)

            if i > j:
                home += p

            elif i == j:
                draw += p

            else:
                away += p

    return home, draw, away