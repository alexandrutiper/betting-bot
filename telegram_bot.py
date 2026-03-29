"""
TELEGRAM BOT MODULE - FINAL VERSION

Acest modul gestionează TOATĂ comunicarea cu Telegram.

RESPONSABILITĂȚI:

✔ trimitere mesaje (send_message)
✔ procesare comenzi utilizator (handle_commands)

DESIGN DECISIONS:

✔ lightweight → nu blocăm execuția botului
✔ fără webhook → simplu polling (suficient pentru Railway)
✔ fail-safe → dacă Telegram pică, botul NU se oprește

IMPORTANT:
Acest modul NU conține logică de business.
Doar comunicare + afișare.
"""

import requests
import config
import db


# ======================================================
# CONFIGURARE API TELEGRAM
# ======================================================

"""
Construim endpoint-ul de bază pentru Telegram API.

Format:
https://api.telegram.org/bot<TOKEN>/
"""

BASE = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}"


# ======================================================
# SEND MESSAGE (FUNCȚIA CENTRALĂ)
# ======================================================

def send_message(text):
    """
    Trimite un mesaj în chat-ul Telegram.

    PARAMETRU:
    - text: string (mesajul de trimis)

    IMPORTANT:
    - folosit în TOT proiectul
    - dacă această funcție nu există → botul crăpa

    PROTECȚIE:
    - try/except → nu vrem ca Telegram să oprească botul
    - timeout → evităm blocaje

    NOTE:
    - folosim POST request (standard Telegram)
    """

    try:

        requests.post(
            f"{BASE}/sendMessage",
            json={
                "chat_id": config.CHAT_ID,
                "text": text
            },
            timeout=10
        )

    except Exception as e:

        # nu oprim botul, doar logăm
        print("Telegram send error:", e)


# ======================================================
# HANDLE COMMANDS (INTERACȚIUNE USER)
# ======================================================

def handle_commands():
    """
    Procesează comenzile primite din Telegram.

    FUNCȚIONARE:

    1. face request la getUpdates
    2. parcurge mesajele primite
    3. identifică comenzile (/bankroll, /dashboard)
    4. trimite răspuns

    IMPORTANT:
    - nu folosim webhook → mai simplu pentru Railway
    - polling ocazional → suficient pentru use-case

    LIMITARE:
    - nu filtrăm update_id (ok pentru bot simplu)
    """

    try:

        response = requests.get(
            f"{BASE}/getUpdates",
            timeout=10
        )

        data = response.json()

    except Exception as e:

        print("Telegram fetch error:", e)
        return

    # ==================================================
    # PARCURGEM TOATE MESAJELE
    # ==================================================

    for update in data.get("result", []):

        message = update.get("message", {})
        text = message.get("text", "")

        # dacă nu e text → ignorăm
        if not text:
            continue

        # ==================================================
        # /bankroll
        # ==================================================

        if text == "/bankroll":

            """
            Returnează bankroll-ul curent.

            Simplu, rapid, fără calcule.
            """

            value = db.get_bankroll()

            send_message(
                f"💰 Bankroll curent: {round(value,2)} lei"
            )

        # ==================================================
        # /dashboard
        # ==================================================

        elif text == "/dashboard":

            """
            Dashboard complet (analytics).

            Afișează:

            ✔ bankroll
            ✔ profit ieri
            ✔ profit 7 zile
            ✔ profit 30 zile
            ✔ ROI global
            ✔ best markets
            ✔ worst markets
            """

            data = db.get_dashboard()

            msg = (
                "📊 DASHBOARD COMPLET\n\n"

                f"💰 Bankroll: {round(data['bankroll'],2)} lei\n"
                f"📅 Profit ieri: {round(data['yesterday'],2)} lei\n"
                f"📈 Profit 7 zile: {round(data['week'],2)} lei\n"
                f"📊 Profit 30 zile: {round(data['month'],2)} lei\n"
                f"💹 ROI global: {round(data['roi']*100,2)}%\n\n"
            )

            # ==============================
            # BEST MARKETS
            # ==============================

            msg += "🔥 BEST MARKETS:\n"

            for bet, roi in data["best"]:

                msg += f"✔ {bet}: {round(roi*100,2)}%\n"

            # ==============================
            # WORST MARKETS
            # ==============================

            msg += "\n❌ WORST MARKETS:\n"

            for bet, roi in data["worst"]:

                msg += f"✖ {bet}: {round(roi*100,2)}%\n"

            send_message(msg)


# ======================================================
# NOTE IMPORTANTE (PENTRU VIITOR)
# ======================================================

"""
Posibile upgrade-uri:

1. Webhook (mai eficient decât polling)
2. Rate limiting (dacă crește volumul)
3. Comenzi noi:
   - /today → picks curente
   - /stats → analytics simplu
   - /top → best bets

Momentan:
✔ suficient
✔ stabil
✔ rapid
"""
