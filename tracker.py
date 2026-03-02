# tracker.py

import json
import os
from datetime import datetime

# folder unde salvăm toate datele
DATA_FOLDER = "data"

# fișiere
PICKS_FILE = "data/picks_history.json"
STATS_FILE = "data/stats.json"


# =====================================================
# CREARE FOLDER DATA
# =====================================================

def ensure_folder():

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)


# =====================================================
# SALVARE PICKS ZILNICE
# =====================================================

def save_picks(picks):

    ensure_folder()

    try:

        with open(PICKS_FILE, "r") as f:
            data = json.load(f)

    except:
        data = []

    entry = {
        "date": datetime.utcnow().isoformat(),
        "picks_found": len(picks),
        "picks": picks
    }

    data.append(entry)

    with open(PICKS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# =====================================================
# STATISTICI SIMPLE
# =====================================================

def update_stats(result):

    """
    result example:
    {
        "profit": 120,
        "tickets": 4,
        "won": 1,
        "lost": 3
    }
    """

    ensure_folder()

    try:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
    except:

        stats = {
            "days": 0,
            "total_profit": 0,
            "tickets": 0,
            "won": 0,
            "lost": 0
        }

    stats["days"] += 1
    stats["total_profit"] += result["profit"]
    stats["tickets"] += result["tickets"]
    stats["won"] += result["won"]
    stats["lost"] += result["lost"]

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)


# =====================================================
# CITIRE STATISTICI
# =====================================================

def get_stats():

    try:

        with open(STATS_FILE) as f:
            return json.load(f)

    except:
        return None