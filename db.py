"""
DATABASE LAYER + ANALYTICS (SQLite)

RESPONSABILITĂȚI:

✔ persistare daily picks
✔ calcul rezultate (win/loss)
✔ update bankroll (DOAR pentru daily picks)
✔ ROI per market (auto-learning)

IMPORTANT:

✔ bankroll NU este folosit pentru bilet cota 2
✔ SQLite → rapid, simplu, perfect pentru Railway
✔ fără ORM → performanță maximă
"""

import sqlite3
from datetime import datetime

DB_FILE = "joker1x.db"


# =====================================================
# INITIALIZARE DB
# =====================================================

def init_db():
    """
    Creează structura DB + inițializează bankroll.

    IMPORTANT DESIGN:

    ✔ NU resetăm bankroll la fiecare run
    ✔ setăm valoare inițială DOAR dacă DB e nou

    SCHIMBARE IMPORTANTĂ:
    👉 bankroll inițial = 200 lei (nu 1000)
    """

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # ===============================
    # DAILY PICKS TABLE
    # ===============================

    c.execute("""
    CREATE TABLE IF NOT EXISTS daily_picks (
        id INTEGER PRIMARY KEY,
        date TEXT,
        match TEXT,
        bet TEXT,
        odds REAL,
        stake REAL,
        result TEXT,
        profit REAL
    )
    """)

    # ===============================
    # BANKROLL TABLE
    # ===============================

    c.execute("""
    CREATE TABLE IF NOT EXISTS bankroll (
        id INTEGER PRIMARY KEY,
        value REAL
    )
    """)

    # ===============================
    # INITIALIZARE BANKROLL
    # ===============================

    """
    LOGICĂ CRITICĂ:

    ✔ verificăm dacă există deja bankroll
    ✔ dacă NU există → setăm 200 lei
    ✔ dacă există → NU modificăm (persistență)

    Asta previne:
    ❌ reset bankroll la fiecare rulare
    """

    c.execute("SELECT COUNT(*) FROM bankroll")
    count = c.fetchone()[0]

    if count == 0:
        c.execute("INSERT INTO bankroll (id, value) VALUES (1, 200)")

    conn.commit()
    conn.close()


# =====================================================
# ROI PER MARKET
# =====================================================

def get_market_roi():

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    SELECT bet, SUM(profit), SUM(stake)
    FROM daily_picks
    WHERE result IS NOT NULL
    GROUP BY bet
    """)

    rows = c.fetchall()

    roi = {}

    for bet, profit, stake in rows:
        if stake and stake > 0:
            roi[bet] = profit / stake
        else:
            roi[bet] = 0

    conn.close()
    return roi


# =====================================================
# SALVARE PICKS
# =====================================================

def save_daily_picks(picks):

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    today = datetime.utcnow().date().isoformat()

    # evităm duplicate
    c.execute("DELETE FROM daily_picks WHERE date=?", (today,))

    for p in picks:
        c.execute("""
        INSERT INTO daily_picks
        (date, match, bet, odds, stake)
        VALUES (?, ?, ?, ?, ?)
        """, (
            today,
            p["match"],
            p["bet"],
            p["odds"],
            p["stake"]
        ))

    conn.commit()
    conn.close()


# =====================================================
# EVALUARE PARIU
# =====================================================

def evaluate_pick(bet, home, away):

    total = home + away

    if bet == "1X":
        return home >= away

    if bet == "X2":
        return away >= home

    if bet == "over15":
        return total >= 2

    if bet == "under45":
        return total <= 4

    return False


# =====================================================
# CHECK RESULTS + UPDATE BANKROLL
# =====================================================

def check_results(scraper):

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    results = scraper.get_scores()

    c.execute("""
    SELECT id, match, bet, odds, stake
    FROM daily_picks
    WHERE result IS NULL
    """)

    rows = c.fetchall()

    total_profit = 0

    for pick_id, match, bet, odds, stake in rows:

        if match not in results:
            continue

        home = results[match]["home"]
        away = results[match]["away"]

        won = evaluate_pick(bet, home, away)

        profit = stake * (odds - 1) if won else -stake

        c.execute("""
        UPDATE daily_picks
        SET result=?, profit=?
        WHERE id=?
        """, (
            "win" if won else "loss",
            round(profit, 2),
            pick_id
        ))

        total_profit += profit

    # ===============================
    # UPDATE BANKROLL (DOAR DAILY PICKS)
    # ===============================

    c.execute("SELECT value FROM bankroll WHERE id=1")
    bankroll = c.fetchone()[0]

    bankroll += total_profit

    c.execute("UPDATE bankroll SET value=? WHERE id=1", (bankroll,))

    conn.commit()
    conn.close()


# =====================================================
# GET BANKROLL
# =====================================================

def get_bankroll():

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT value FROM bankroll WHERE id=1")
    value = c.fetchone()[0]

    conn.close()

    return value


# =====================================================
# YESTERDAY RESULTS
# =====================================================

def get_yesterday_results():

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    SELECT match, bet, result, profit
    FROM daily_picks
    WHERE date = date('now','-1 day')
    """)

    rows = c.fetchall()

    total_profit = sum(r[3] for r in rows if r[3] is not None)

    conn.close()

    return rows, total_profit


# =====================================================
# DASHBOARD
# =====================================================

def get_dashboard():

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT value FROM bankroll WHERE id=1")
    bankroll = c.fetchone()[0]

    c.execute("""
    SELECT SUM(profit)
    FROM daily_picks
    WHERE date = date('now','-1 day')
    """)
    yesterday = c.fetchone()[0] or 0

    c.execute("""
    SELECT SUM(profit)
    FROM daily_picks
    WHERE date >= date('now','-7 day')
    """)
    week = c.fetchone()[0] or 0

    c.execute("""
    SELECT SUM(profit)
    FROM daily_picks
    WHERE date >= date('now','-30 day')
    """)
    month = c.fetchone()[0] or 0

    c.execute("""
    SELECT SUM(profit), SUM(stake)
    FROM daily_picks
    WHERE result IS NOT NULL
    """)
    profit, stake = c.fetchone()

    roi = (profit / stake) if stake else 0

    c.execute("""
    SELECT bet, SUM(profit)/SUM(stake)
    FROM daily_picks
    WHERE result IS NOT NULL
    GROUP BY bet
    """)

    markets = c.fetchall()
    conn.close()

    markets = sorted(markets, key=lambda x: x[1], reverse=True)

    return {
        "bankroll": bankroll,
        "yesterday": yesterday,
        "week": week,
        "month": month,
        "roi": roi,
        "best": markets[:3],
        "worst": markets[-3:]
    }
