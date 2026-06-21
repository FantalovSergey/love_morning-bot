import logging
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher

from .dotenv_validation import get_env_vars
from .middlewares import AccessMiddleware

TZ = timezone(timedelta(hours=10), 'Asia/Vladivostok')
logging.Formatter.converter = lambda *_: datetime.now(TZ).timetuple()

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

bot = Bot(BOT_TOKEN)
dispatcher = Dispatcher()
dispatcher.message.outer_middleware(AccessMiddleware(ARINA_ID, MY_ID))

LOVE_MESSAGES_FILEPATH = '/data/love_messages.txt'
DREAMS_FILEPATH = '/data/dreams.txt'

SENDING_TIME = {
    'hour': 6,
    'minute': 0,
    'second': 0,
    'microsecond': 0,
}
DAY_PARTS_EXCEPT_MORNING: (
    tuple[tuple[tuple[int, ...], str], tuple[range, str], tuple[range, str]]
) = (
    (tuple(range(4)) + tuple(range(23, 24)), 'Спокойной ночи'),
    (range(12, 16), 'Добрый день'),
    (range(16, 23), 'Добрый вечер'),
)
"""
Содержит диапазоны часов, соответствующие времени суток,
и приветственные фразы, например 'Добрый вечер'.
"""

START_MESSAGE = (
    'Приветище! Каждое утро я буду присылать тебе что-нибудь милое😊. '
    'Если хочешь этого прямо сейчас, жми на левую верхнюю кнопочку. '
    'Я глупенький, поэтому не смогу понимать твои сообщения '
    'и буду пересылать их моему создателю. Там, конечно, тоже не гений сидит, '
    'но у него больше шансов разобраться✨ Также ты можешь делиться с нами '
    'своими снами, мы будем очень рады🤗 В любой момент ты можешь '
    'посмотреть все сны или удалить те, которые захочешь🙌'
)

FROM_BOT_MESSAGE_SYMBOL_LIMIT = 3072
TO_BOT_MESSAGE_SYMBOL_LIMIT = 3000

CONTENT_SHOWING_PERIOD = 600
