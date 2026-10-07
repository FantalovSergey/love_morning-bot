import logging
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler

from aiogram import Bot

from love_bot.env import get_env_vars

TZ = timezone(timedelta(hours=10), 'Asia/Vladivostok')

logging.Formatter.converter = lambda *_: datetime.now(TZ).timetuple()
handler = RotatingFileHandler('/data/logs.log', maxBytes=500000, backupCount=5)
handler.setFormatter(
    logging.Formatter('%(asctime)s %(levelname)s %(message)s'),
)
logger = logging.getLogger(__name__)
logger.addHandler(handler)

try:
    BOT_TOKEN, ARINA_ID, MY_ID = get_env_vars()
except ValueError as absent_env_vars_error:
    logger.critical(absent_env_vars_error)
    raise

bot = Bot(BOT_TOKEN)

LOVE_MESSAGES_FILEPATH = '/data/love_messages.txt'
DREAMS_FILEPATH = '/data/dreams.txt'

SENDING_TIME = {
    'hour': 6,
    'minute': 0,
    'second': 0,
    'microsecond': 0,
}

GREETINGS_EXCEPT_MORNING: tuple[tuple[range, str], ...] = (
    (range(4), 'Спокойной ночи'),
    (range(12, 16), 'Добрый день'),
    (range(16, 23), 'Добрый вечер'),
    (range(23, 24), 'Спокойной ночи'),
)
"""
Содержит диапазоны часов, соответствующие времени суток,
и приветственные фразы, например 'Добрый вечер'.
"""

WRITING_CONTENT_SYMBOL_LIMIT = 4000
TELEGRAM_MESSAGE_SYMBOL_LIMIT = 4096

DELETING_MESSAGE_COUNT_LIMIT = 100

FILE_OPENING_ATTEMPTS_LIMIT = 3

CONTENT_SHOWING_PERIOD = 300
