"""
Project settings
"""
import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN',
                               '6579017739:AAGDB0C0CEywwshGnzoD7nSVWhp7icOXHfc')

if not TELEGRAM_BOT_TOKEN:
    raise ImportError("Error import telegram bot token")
