
# config.py

"""
CONFIGURAȚII GENERALE BOT
"""

# ==========================================================
# TELEGRAM & API
# ==========================================================

import os

# Citim valorile din environment variables (Railway)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

# =====================================================
# INTERVAL ANALIZĂ
# =====================================================

# Analizăm meciurile din următoarele X ore
MATCH_WINDOW_HOURS = 12

# =====================================================
# STRATEGIE BILETE
# =====================================================

STAKE = 100
TICKETS_PER_DAY = 3

MIN_TOTAL_ODDS = 3.3
MAX_TOTAL_ODDS = 5.0

MIN_MATCHES_PER_TICKET = 3
MAX_MATCHES_PER_TICKET = 4

MIN_PORTFOLIO_WIN_CHANCE = 0.60

# =====================================================
# FILTRARE DAILY PICKS (STRICT)
# =====================================================

MIN_PROBABILITY_STRICT = 0.60
MIN_STRENGTH_STRICT = 1.35
CONSENSUS_THRESHOLD_STRICT = 0.25

# =====================================================
# FILTRARE OPTIMIZER (RELAXED)
# =====================================================

MIN_PROBABILITY_RELAXED = 0.50
MIN_STRENGTH_RELAXED = 1.15

# =====================================================
# OPTIMIZER
# =====================================================

SIMULATIONS = 100000

# =====================================================
# BANKROLL
# =====================================================

START_BANKROLL = 1000
DATA_FOLDER = "data"
