# storage.py

import json
import os
from datetime import datetime

DATA_FOLDER = "data"

TICKETS_FILE = "data/tickets.json"
BANKROLL_FILE = "data/bankroll.json"


# =====================================================
# CREARE FOLDER
# =====================================================

def ensure_folder():
    """
    Asigură existența folderului unde salvăm datele.
    """

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)


# =====================================================
# LOAD JSON
# =====================================================

def load_json(path):
    """
    Citește un fișier JSON dacă există.
    """

    if not os.path.exists(path):
        return None

    with open(path) as f:
        return json.load(f)


# =====================================================
# SAVE JSON
# =====================================================

def save_json(path, data):
    """
    Salvează date JSON în fișier.
    """

    ensure_folder()

    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# =====================================================
# SALVARE BILETE ZILNICE
# =====================================================

def save_daily_tickets(tickets):
    """
    Salvează biletele generate astăzi.

    Dacă botul rulează de mai multe ori în aceeași zi,
    entry-ul este suprascris (nu duplicat).
    """

    ensure_folder()

    data = load_json(TICKETS_FILE)

    if not data:
        data = []

    today = datetime.utcnow().date().isoformat()

    # verificăm dacă există deja o intrare azi
    for entry in data:

        if entry["date"] == today:

            entry["tickets"] = tickets
            entry["checked"] = False

            save_json(TICKETS_FILE, data)
            return

    # dacă nu există intrare pentru azi, creăm una
    entry = {
        "date": today,
        "tickets": tickets,
        "checked": False
    }

    data.append(entry)

    save_json(TICKETS_FILE, data)


# =====================================================
# CITIRE BILETE
# =====================================================

def get_tickets():
    """
    Returnează istoricul biletelor.
    """

    data = load_json(TICKETS_FILE)

    if not data:
        return []

    return data


# =====================================================
# UPDATE DUPĂ VERIFICARE
# =====================================================

def mark_checked(index, result):
    """
    Marchează ziua ca verificată
    și salvează profitul acelei zile.
    """

    data = load_json(TICKETS_FILE)

    if not data:
        return

    data[index]["checked"] = True
    data[index]["result"] = result

    save_json(TICKETS_FILE, data)


# =====================================================
# BANKROLL
# =====================================================

def get_bankroll():
    """
    Returnează banca actuală.
    Creează fișierul dacă nu există.
    """

    data = load_json(BANKROLL_FILE)

    if not data:

        data = {
            "bankroll": 1000,
            "history": []
        }

        save_json(BANKROLL_FILE, data)

    return data


# =====================================================
# UPDATE BANKROLL
# =====================================================

def update_bankroll(profit):
    """
    Actualizează banca după rezultatele unei zile.
    """

    data = get_bankroll()

    data["bankroll"] += profit

    data["history"].append({

        "date": datetime.utcnow().isoformat(),
        "profit": profit
    })

    save_json(BANKROLL_FILE, data)

    return data["bankroll"]
