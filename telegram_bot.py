
"""
TELEGRAM BOT

Trimite mesajele către Telegram.
"""

import requests
import config


def send_message(text):

    url=f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"

    payload={

        "chat_id":config.CHAT_ID,
        "text":text
    }

    requests.post(url,json=payload)