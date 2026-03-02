# leagues.py


# =====================================================
# PRIORITY LEVELS
# =====================================================
# 3 = foarte de încredere
# 2 = bun
# 1 = fallback / zile slabe

LEAGUE_PRIORITY = {


    # =================================================
    # EUROPA TOP (PRIORITATE MAXIMA)
    # =================================================

    "soccer_epl": 3,
    "soccer_spain_la_liga": 3,
    "soccer_italy_serie_a": 3,
    "soccer_germany_bundesliga": 3,
    "soccer_france_ligue_one": 3,



    # =================================================
    # EUROPA LIGI SECUNDE
    # =================================================

    "soccer_efl_championship": 3,
    "soccer_spain_segunda_division": 2,
    "soccer_italy_serie_b": 2,
    "soccer_germany_bundesliga2": 2,
    "soccer_france_ligue_two": 2,



    # =================================================
    # EUROPA MID TIERS
    # =================================================

    "soccer_netherlands_eredivisie": 3,
    "soccer_portugal_primeira_liga": 3,
    "soccer_belgium_first_div": 3,
    "soccer_turkey_super_league": 3,



    # =================================================
    # SCANDINAVIA
    # =================================================

    "soccer_sweden_allsvenskan": 2,
    "soccer_norway_eliteserien": 2,
    "soccer_denmark_superliga": 2,



    # =================================================
    # ALTE LIGI EUROPENE
    # =================================================

    "soccer_switzerland_superleague": 2,
    "soccer_austria_bundesliga": 2,



    # =================================================
    # UEFA
    # =================================================

    "soccer_uefa_champs_league": 3,
    "soccer_uefa_europa_league": 3,
    "soccer_uefa_europa_conference_league": 3,

    "soccer_uefa_nations_league": 3,
    "soccer_uefa_euro_qualification": 3,



    # =================================================
    # AMERICA DE SUD
    # =================================================

    "soccer_brazil_campeonato": 3,
    "soccer_brazil_serie_b": 2,

    "soccer_argentina_primera_division": 3,
    "soccer_chile_primera_division": 2,
    "soccer_colombia_primera_a": 2,



    # =================================================
    # AMERICA DE NORD
    # =================================================

    "soccer_mexico_ligamx": 3,
    "soccer_usa_mls": 2,



    # =================================================
    # ASIA
    # =================================================

    "soccer_japan_j_league": 2,
    "soccer_korea_kleague1": 2,



    # =================================================
    # AUSTRALIA
    # =================================================

    "soccer_australia_aleague": 2,
}



# =====================================================
# LISTA FOLOSITA DE BOT
# =====================================================

ALLOWED_LEAGUES = list(LEAGUE_PRIORITY.keys())



# =====================================================
# NUME + EMOJI
# =====================================================

LEAGUE_NAMES = {

    "soccer_epl": ("Premier League", "🇬🇧"),
    "soccer_efl_championship": ("Championship", "🇬🇧"),

    "soccer_spain_la_liga": ("La Liga", "🇪🇸"),
    "soccer_spain_segunda_division": ("La Liga 2", "🇪🇸"),

    "soccer_italy_serie_a": ("Serie A", "🇮🇹"),
    "soccer_italy_serie_b": ("Serie B", "🇮🇹"),

    "soccer_germany_bundesliga": ("Bundesliga", "🇩🇪"),
    "soccer_germany_bundesliga2": ("Bundesliga 2", "🇩🇪"),

    "soccer_france_ligue_one": ("Ligue 1", "🇫🇷"),
    "soccer_france_ligue_two": ("Ligue 2", "🇫🇷"),

    "soccer_netherlands_eredivisie": ("Eredivisie", "🇳🇱"),

    "soccer_portugal_primeira_liga": ("Primeira Liga", "🇵🇹"),

    "soccer_belgium_first_div": ("Belgian Pro League", "🇧🇪"),

    "soccer_turkey_super_league": ("Super Lig", "🇹🇷"),

    "soccer_sweden_allsvenskan": ("Allsvenskan", "🇸🇪"),
    "soccer_norway_eliteserien": ("Eliteserien", "🇳🇴"),
    "soccer_denmark_superliga": ("Superliga", "🇩🇰"),

    "soccer_switzerland_superleague": ("Swiss Super League", "🇨🇭"),
    "soccer_austria_bundesliga": ("Austrian Bundesliga", "🇦🇹"),

    "soccer_uefa_champs_league": ("Champions League", "⭐"),
    "soccer_uefa_europa_league": ("Europa League", "🟠"),
    "soccer_uefa_europa_conference_league": ("Conference League", "🟢"),

    "soccer_uefa_nations_league": ("Nations League", "🌍"),
    "soccer_uefa_euro_qualification": ("Euro Qualifiers", "🏆"),

    "soccer_brazil_campeonato": ("Brazil Serie A", "🇧🇷"),
    "soccer_brazil_serie_b": ("Brazil Serie B", "🇧🇷"),

    "soccer_argentina_primera_division": ("Argentina Primera", "🇦🇷"),
    "soccer_chile_primera_division": ("Chile Primera", "🇨🇱"),
    "soccer_colombia_primera_a": ("Colombia Primera A", "🇨🇴"),

    "soccer_mexico_ligamx": ("Liga MX", "🇲🇽"),
    "soccer_usa_mls": ("MLS", "🇺🇸"),

    "soccer_japan_j_league": ("J League", "🇯🇵"),
    "soccer_korea_kleague1": ("K League", "🇰🇷"),

    "soccer_australia_aleague": ("A-League", "🇦🇺"),
}