# telegram_bot.py

import requests
import config
import re
import time


# =====================================================
# TELEGRAM LIMIT
# =====================================================

MAX_MESSAGE = 4000


# =====================================================
# ESCAPE MARKDOWN V2
# =====================================================

def escape_markdown(text):

    escape_chars = r"_*[]()~`>#+-=|{}.!"

    return re.sub(
        f"([{re.escape(escape_chars)}])",
        r"\\\1",
        text
    )


# =====================================================
# TRIMITERE REQUEST TELEGRAM
# =====================================================

def _send(payload):

    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"

    try:

        r = requests.post(url, json=payload, timeout=10)

        # rate limit
        if r.status_code == 429:
            time.sleep(2)
            r = requests.post(url, json=payload, timeout=10)

        if r.status_code != 200:
            print("Telegram error:", r.text)

    except Exception as e:

        print("Telegram connection error:", e)


# =====================================================
# SPLIT MESAJ LUNG
# =====================================================

def split_message(text):

    parts = []

    while len(text) > MAX_MESSAGE:

        part = text[:MAX_MESSAGE]

        # tăiem la newline pentru a nu rupe textul
        last_break = part.rfind("\n")

        if last_break != -1:
            part = part[:last_break]

        parts.append(part)

        text = text[len(part):]

    parts.append(text)

    return parts


# =====================================================
# FUNCTIA PUBLICĂ
# =====================================================

def send_message(text):

    safe_text = escape_markdown(text)

    parts = split_message(safe_text)

    for part in parts:

        payload = {
            "chat_id": config.CHAT_ID,
            "text": part,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": True
        }

        _send(payload)

        time.sleep(0.3)