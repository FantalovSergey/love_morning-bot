import logging
from datetime import timedelta, timezone
from logging.handlers import RotatingFileHandler
from typing import Iterable

from aiogram import Bot, Dispatcher

from .dotenv_validation import get_env_vars
from .middlewares import AccessMiddleware

format = '%(asctime)s %(levelname)s %(message)s'
handler = RotatingFileHandler('/data/logs.log', maxBytes=500000, backupCount=5)
handler.setFormatter(logging.Formatter(format))
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

try:
    BOT_TOKEN, ARINA_ID, MY_ID = get_env_vars()
except ValueError as absent_env_vars_error:
    logger.critical(absent_env_vars_error)
    raise absent_env_vars_error

LOVE_MESSAGES_FILEPATH = '/data/love_messages.txt'
DREAMS_FILEPATH = '/data/dreams.txt'

FROM_BOT_MESSAGE_SYMBOL_LIMIT = 3072
TO_BOT_MESSAGE_SYMBOL_LIMIT = 3000

TZ = timezone(timedelta(hours=10), 'Asia/Vladivostok')

SENDING_TIME = {
    'hour': 6,
    'minute': 0,
    'second': 0,
    'microsecond': 0,
}

DAY_PARTS_EXCEPT_MORNING: tuple[tuple[Iterable[int], str]] = (
    (tuple(range(4)) + tuple(range(23, 24)), 'Спокойноной ночи'),
    (range(12, 16), 'Добрый день'),
    (range(16, 23), 'Добрый вечер'),
)
"""
Содержит диапазоны часов, соответствующие времени суток,
и приветсвенные фразы, например 'Добрый вечер'.
"""

bot = Bot(BOT_TOKEN)
dispatcher = Dispatcher()
dispatcher.update.outer_middleware(AccessMiddleware((ARINA_ID, MY_ID)))
