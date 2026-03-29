
"""
MARKET CONVERTER

Transformă codurile interne în text prietenos.
"""

def convert(bet):

    mapping={

        "1X":"1X – Gazdele sau egal",
        "X2":"X2 – Oaspeți sau egal",

        "home_dnb":"DNB 1 – Gazdele",
        "away_dnb":"DNB 2 – Oaspeții",

        "over15":"Peste 1.5 goluri",
        "under45":"Sub 4.5 goluri",

        "goals_1_4":"1-4 goluri",
        "goals_2_6":"2-6 goluri",

        "over15":"Peste 1.5 goluri",
        "under45":"Sub 4.5 goluri"

    }

    return mapping.get(bet,bet)
