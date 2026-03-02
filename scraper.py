# scraper.py

import requests
import config
import leagues


def get_matches():

    matches = []

    # =====================================================
    # PARCURGEM TOATE LIGILE
    # =====================================================

    for league in leagues.ALLOWED_LEAGUES:

        url = f"https://api.the-odds-api.com/v4/sports/{league}/odds"

        params = {
            "apiKey": config.ODDS_API_KEY,
            "regions": "eu",
            "markets": "h2h,totals",
            "oddsFormat": "decimal"
        }

        try:

            response = requests.get(url, params=params, timeout=10)

        except Exception as e:

            print("Request failed:", league)
            continue

        if response.status_code != 200:

            print("API error:", league)
            continue

        data = response.json()

        # =====================================================
        # FIECARE ELEMENT = UN MECI
        # =====================================================

        for game in data:

            try:

                home = game["home_team"]
                away = game["away_team"]

                commence_time = game.get("commence_time")

                bookmakers = game.get("bookmakers", [])

                # dacă sunt prea puține case -> ignorăm
                if len(bookmakers) < 2:
                    continue

                odds_home = []
                odds_draw = []
                odds_away = []

                odds_over15 = []

                # =================================================
                # COLECTĂM COTE DE LA TOATE CASELE
                # =================================================

                for book in bookmakers:

                    markets = book.get("markets", [])

                    for market in markets:

                        key = market.get("key")

                        # -----------------------------------------
                        # 1X2 MARKET
                        # -----------------------------------------

                        if key == "h2h":

                            for o in market.get("outcomes", []):

                                name = o.get("name")
                                price = o.get("price")

                                if name == home:
                                    odds_home.append(price)

                                elif name == away:
                                    odds_away.append(price)

                                else:
                                    odds_draw.append(price)

                        # -----------------------------------------
                        # TOTAL GOALS
                        # -----------------------------------------

                        if key == "totals":

                            for o in market.get("outcomes", []):

                                if (
                                    o.get("name") == "Over"
                                    and o.get("point") == 1.5
                                ):
                                    odds_over15.append(o.get("price"))

                # =================================================
                # VALIDARE DATE
                # =================================================

                if not odds_home or not odds_away:
                    continue

                # =================================================
                # MEDIILE COTELOR
                # =================================================

                avg_home = sum(odds_home) / len(odds_home)
                avg_away = sum(odds_away) / len(odds_away)

                avg_draw = (
                    sum(odds_draw) / len(odds_draw)
                    if odds_draw else None
                )

                avg_over15 = (
                    sum(odds_over15) / len(odds_over15)
                    if odds_over15 else None
                )

                # =================================================
                # CONSENSUS (dezacord între case)
                # =================================================

                consensus = max(odds_home) - min(odds_home)

                # =================================================
                # STRUCTURA MECIULUI
                # =================================================

                match = {

                    "league": league,

                    "home": home,
                    "away": away,

                    "commence_time": commence_time,

                    "odds": {
                        "1": avg_home,
                        "X": avg_draw,
                        "2": avg_away
                    },

                    "goals": {
                        "over15": avg_over15
                    },

                    "consensus": consensus
                }

                matches.append(match)

            except Exception:
                continue

    return matches

# =====================================================
# REZULTATE MECIURI
# =====================================================

def get_scores():

    import requests
    import leagues
    import config

    results = {}

    for league in leagues.ALLOWED_LEAGUES:

        url = f"https://api.the-odds-api.com/v4/sports/{league}/scores"

        params = {
            "apiKey": config.ODDS_API_KEY,
            "daysFrom": 1
        }

        r = requests.get(url, params=params)

        if r.status_code != 200:
            continue

        data = r.json()

        for game in data:

            if not game.get("completed"):
                continue

            home = game["home_team"]
            away = game["away_team"]

            scores = game.get("scores")

            if not scores:
                continue

            try:

                home_score = int(scores[0]["score"])
                away_score = int(scores[1]["score"])

                match_name = f"{home} vs {away}"

                results[match_name] = {

                    "home": home_score,
                    "away": away_score
                }

            except:
                continue

    return results