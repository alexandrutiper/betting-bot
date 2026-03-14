
"""
CONFIGURAȚII GENERALE BOT

Acest fișier conține toți parametrii strategiei.
Modificarea acestora permite ajustarea rapidă a botului
fără modificarea codului principal.
"""

# ======================================================
# TELEGRAM
# ======================================================

# Token Telegram (obligatoriu pentru funcționare bot)
TELEGRAM_TOKEN = "8655935129:AAEje7CUsVTK5AHkQb3tniPk5PgsaSVhAPQ"

# Chat ID unde trimite mesajele
CHAT_ID = "6846683629"

# ======================================================
# ODDS API
# ======================================================

ODDS_API_KEY = "21ff2c49824165e71d5444bec23196e1"

# ======================================================
# FEREASTRA MECIURI
# ======================================================

MATCH_WINDOW_HOURS = 12

# ======================================================
# STRATEGIE BILET
# ======================================================

MIN_TOTAL_ODDS = 1.98
MAX_TOTAL_ODDS = 2.25

MIN_MATCHES_PER_TICKET = 4
MAX_MATCHES_PER_TICKET = 7

# ======================================================
# FILTRARE SELECȚII
# ======================================================

MIN_SELECTION_PROB = 0.78
MAX_SELECTION_ODDS = 1.28

# ======================================================
# MONTE CARLO
# ======================================================

SIMULATIONS = 300000

# ======================================================
# DAILY PICKS
# ======================================================

DAILY_PICKS = 10
DAILY_MIN_PROB = 0.77
MIN_DAILY_ODDS = 1.15

# ======================================================
# OPTIMIZER PERFORMANCE
# ======================================================

"""
Numărul maxim de selecții candidate
păstrate în pool.

Reducerea pool-ului reduce dramatic
numărul de combinații.
"""

POOL_LIMIT = 40


"""
Numărul de bilete candidate
evaluate cu Monte Carlo.
"""

FINAL_TICKET_CANDIDATES = 15