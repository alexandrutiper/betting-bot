
# config.py

"""
CONFIGURAȚII GENERALE BOT
"""

# ==========================================================
# TELEGRAM & API
# ==========================================================

# Token Telegram (obligatoriu pentru funcționare bot)
TELEGRAM_TOKEN = "8655935129:AAEje7CUsVTK5AHkQb3tniPk5PgsaSVhAPQ"

# Chat ID unde trimite mesajele
CHAT_ID = "6846683629"

# API key pentru The Odds API
ODDS_API_KEY = "21ff2c49824165e71d5444bec23196e1"

# ==========================================================
# FEREASTRĂ ANALIZĂ MECIURI
# ==========================================================

"""
Analizăm meciurile care încep în următoarele 12 ore.
Botul rulează de două ori pe zi.
"""

MATCH_WINDOW_HOURS = 12

# ==========================================================
# STRATEGIE BILET
# ==========================================================

"""
Strategia urmărește un bilet cotă ~2
cu probabilitate reală cât mai mare.

Pentru a obține probabilitate mare:
• folosim multe selecții sigure
• evităm cote mari individuale
"""

MIN_TOTAL_ODDS = 1.98
MAX_TOTAL_ODDS = 2.25

MIN_MATCHES_PER_TICKET = 5
MAX_MATCHES_PER_TICKET = 7

# ==========================================================
# FILTRARE SELECȚII
# ==========================================================

"""
Selecțiile candidate trebuie să fie foarte sigure.

Probabilitatea minimă a unei selecții.
"""

MIN_SELECTION_PROB = 0.78

"""
Limităm cota maximă per selecție pentru a evita
pariurile riscante.
"""

MAX_SELECTION_ODDS = 1.28

"""
Forță minimă a favoritului în piață.
"""

MIN_MARKET_STRENGTH = 1.25

# ==========================================================
# MONTE CARLO
# ==========================================================

"""
Simulări Monte Carlo pentru estimarea probabilității
de câștig a biletului.
"""

SIMULATIONS = 300000

# ==========================================================
# DAILY PICKS
# ==========================================================

"""
Daily Picks sunt separate de optimizer.

Sunt doar recomandări orientative
cu probabilitate foarte mare.
"""

DAILY_PICKS = 10
DAILY_MIN_PROB = 0.75