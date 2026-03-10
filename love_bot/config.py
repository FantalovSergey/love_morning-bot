import logging
from datetime import timedelta, timezone
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher

from .dotenv_validation import check_necessary_env_vars

format = '%(asctime)s %(levelname)s %(message)s'
handler = RotatingFileHandler('/data/logs.log', maxBytes=500000, backupCount=5)
handler.setFormatter(logging.Formatter(format))
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

try:
    BOT_TOKEN, ARINA_ID, MY_ID = check_necessary_env_vars().values()
except ValueError as absent_env_vars_error:
    logger.critical(absent_env_vars_error)
    raise ValueError(absent_env_vars_error)


FOR_UNKNOWN_USERS = (
    'Доброго времени суток! Этот бот предназначен исключительно '
    'для одного человека, для Арины Атаманюк. Если Вы её знаете, '
    'передайте ей привет🖐️'
)

FILEPATH = '/data/message_bank.txt'

BOT_MESSAGE_SYMBOL_LIMIT = 1024

TZ = timezone(timedelta(hours=10), 'Asia/Vladivostok')
SENDING_TIME = {
    'hour': 6,
    'minute': 0,
    'second': 0,
    'microsecond': 0,
}

RETRY_PERIOD = 180

bot = Bot(BOT_TOKEN)
dispatcher = Dispatcher()
