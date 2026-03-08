# ==========================================================
# CONVERSIE MARKETURI -> FORMAT SUPERBET
# ==========================================================

"""
Acest fișier transformă denumirile interne ale botului
în denumirile folosite de Superbet.

Exemplu:

1X -> "1X – Gazdele sau egal"
home_dnb -> "DNB 1 – Gazdele"
over15 -> "Peste 1.5 goluri"
"""

def convert_market(bet):

    mapping = {

        "1": "1 – Gazdele câștigă",

        "2": "2 – Oaspeții câștigă",

        "1X": "1X – Gazdele sau egal",

        "X2": "X2 – Oaspeți sau egal",

        "12": "12 – Fără egal",

        "home_dnb": "DNB 1 – Gazdele",

        "away_dnb": "DNB 2 – Oaspeții",

        "over15": "Peste 1.5 goluri",

        "under45": "Sub 4.5 goluri"

    }

    return mapping.get(bet, bet)