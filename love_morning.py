import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from random import choice

from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramNetworkError, TelegramServerError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup
from dotenv import load_dotenv

import keyboards
from exceptions import UnexpectedError
from fsms import DeleteMessages
from utils import get_indexes

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ARINA_ID = int(os.getenv('ARINA_ID'))
MY_ID = int(os.getenv('MY_ID'))
FOR_UNKNOWN_USERS = (
    'Доброго времени суток! Этот бот предназначен исключительно '
    'для одного человека, для Арины Атаманюк. Если Вы её знаете, '
    'передайте ей привет🖐️'
)

FILENAME = '/data/messages.txt'
TG_SYMBOL_LIMIT = 4096

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
is_sending_available = os.getenv('IS_SENDING_AVAILABLE') == 'True'

format = '%(asctime)s %(levelname)s %(message)s'
handler = RotatingFileHandler('/data/logs.log', maxBytes=500000, backupCount=5)
handler.setFormatter(logging.Formatter(format))
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


def check_necessary_env_vars():
    """
    Проверяет обязательные переменные окружения.

    Бот будет остановлен при отсутствии.
    """
    env_vars = {
        'BOT_TOKEN': BOT_TOKEN,
        'ARINA_ID': ARINA_ID,
        'MY_ID': MY_ID,
    }
    absent_env_vars = [key for key, var in env_vars.items() if var is None]
    if absent_env_vars:
        env_vars_error = (
            'Отсутствуют следующие обязательные переменные окружения: '
            f'"{', '.join(absent_env_vars)}". Бот остановлен.'
        )
        logger.critical(env_vars_error)
        raise ValueError(env_vars_error)


async def safe_send_message(chat_id: int, message: str):
    """
    Отправка сообщений по указанному id пользователя.

    Повторная отправка при ошибках подключения к Telegram.

    Остановка бота при неожиданных ошибках.
    """
    while True:
        try:
            await bot.send_message(chat_id, message)
        except (TelegramNetworkError, TelegramServerError):
            logger.exception('Сбой при отправке сообщения в Telegram.')
            await asyncio.sleep(RETRY_PERIOD)
        except Exception as error:
            unexpected_error = (
                'Мы не знаем, что это такое, если бы мы знали, что это такое, '
                f'мы не знаем, что это такое:\n{error}'
            )
            logger.exception(unexpected_error)
            raise UnexpectedError(unexpected_error)
        else:
            if chat_id == ARINA_ID:
                await bot.send_message(MY_ID, f'Отправлено:\n{message}')
            break


async def get_love_messages_from_file() -> list[str] | None:
    """
    Получения всех сообщений из файла.

    Логирование ошибок отсутствия самого файла или его содержимого.
    """
    file_error = None
    try:
        with open(FILENAME, encoding='utf-8') as file:
            love_messages = file.readlines()
    except FileNotFoundError:
        file_error = 'Файл с сообщениями не найден'
    else:
        if not love_messages:
            file_error = 'Файл с сообщениями пуст'
        else:
            return love_messages
    finally:
        if file_error:
            logger.error(file_error)
            await safe_send_message(MY_ID, file_error)


async def send_love_message():
    """
    Отправка сообщения Арине.

    Если есть проблемы с файлом, бот извиняется.
    """
    love_messages = await get_love_messages_from_file()
    if not love_messages:
        await safe_send_message(
            ARINA_ID,
            (
                'Я не могу тебе ничего отправить😢\n'
                'Прости, пожалуйста🙏\n'
                'Я написал Серёже, он попробует всё починить'
            ),
        )
    else:
        await safe_send_message(ARINA_ID, choice(love_messages))


async def show_messages(
    love_messages: list[str], keyboard: ReplyKeyboardMarkup
):
    """
    Отправка списка сообщений вместе с клавиатурой по моему запросу.

    Учитывается лимит символов Telegram для одного сообщения.
    """
    chunk = []
    symbol_count = 0
    for index, love_message in enumerate(love_messages):
        # индекс + точка + пробел + перенос строки в конце = 4
        symbol_count += len(love_message) + 4
        if symbol_count > TG_SYMBOL_LIMIT:
            symbol_count = 0
            await bot.send_message(MY_ID, ''.join(chunk))
            chunk = []
        chunk.append(f'{index}. {love_message}')
    await bot.send_message(MY_ID, ''.join(chunk), reply_markup=keyboard)


async def wish_good_morning():
    """Пожелание доброго утра каждый день в определённое время."""
    while True:
        now = datetime.now(TZ)
        delta = now.replace(**SENDING_TIME) - now
        # Если дельта отрицательная, свойство seconds вернёт количество секунд
        # до момента отправки, которая произойдёт на следующий день
        await asyncio.sleep(delta.seconds)
        if is_sending_available:
            await send_love_message()
        await asyncio.sleep(1)


@dispatcher.message(Command("start"))
async def start(message: Message):
    global is_sending_available
    if message.chat.id == ARINA_ID:
        first_message = (
            'Приветище! Каждое утро я буду присылать тебе что-нибудь милое😊. '
            'Если хочешь этого прямо сейчас, жми на кнопочку. Я глупенький, '
            'поэтому не смогу понимать твои сообщения и буду пересылать их '
            'моему создателю. Там, конечно, тоже не гений сидит, '
            'но у него больше шансов разобраться✨'
        )
        await message.answer(
            first_message, reply_markup=keyboards.get_cuteness,
        )
        is_sending_available = True
    elif message.chat.id == MY_ID:
        await message.answer('🖐️', reply_markup=keyboards.show_messages)
    else:
        await message.answer(FOR_UNKNOWN_USERS)


@dispatcher.message(F.text == keyboards.GET_CUTENESS_TEXT)
async def send_cuteness_immediately(message: Message):
    if message.chat.id == ARINA_ID:
        await send_love_message()


@dispatcher.message(F.text == keyboards.SHOW_MESSAGES_TEXT)
async def show_all_messages(message: Message):
    if message.chat.id == MY_ID:
        love_messages = await get_love_messages_from_file()
        if love_messages:
            await show_messages(love_messages, keyboards.delete_messages)
    if message.chat.id == ARINA_ID:
        await message.answer('Вы делаете что-то незаконное🤔')


@dispatcher.message(F.text == keyboards.DELETE_MESSAGES_TEXT)
async def start_messages_deleting(message: Message, state: FSMContext):
    if message.chat.id == MY_ID:
        await state.clear()
        await message.answer(
            (
                'Введите диапазоны сообщений через запятую\n'
                'Пример: 1, 17-19, 23-24'
            ),
            reply_markup=keyboards.cancel
        )
        await state.set_state(DeleteMessages.indexes)
    if message.chat.id == ARINA_ID:
        await message.answer('Вы делаете что-то очень незаконное🤔🤔🤔')


@dispatcher.message(DeleteMessages.indexes)
async def delete_messages(message: Message, state: FSMContext):
    if message.text == keyboards.CANCEL_TEXT:
        await state.clear()
        await message.answer(
            'Удаление отменено', reply_markup=keyboards.show_messages
        )
    else:
        try:
            indexes_for_deleting = get_indexes(message.text)
        except ValueError:
            await message.answer('Проверьте правильность ввода')
        else:
            love_messages = await get_love_messages_from_file()
            if love_messages:
                with open(FILENAME, 'w', encoding='utf-8') as file:
                    undeleted_messages = []
                    deleted_messages = []
                    for index, love_message in enumerate(love_messages):
                        (
                            deleted_messages.append(love_message)
                            if index in indexes_for_deleting
                            else undeleted_messages.append(love_message)
                        )
                    file.writelines(undeleted_messages)
                await message.answer('Удалены следующие сообщения:')
                await show_messages(deleted_messages, keyboards.show_messages)
                await state.clear()


@dispatcher.message()
async def receive_message(message: Message):
    if message.chat.id == ARINA_ID:
        await bot.forward_message(
            chat_id=MY_ID,
            from_chat_id=ARINA_ID,
            message_id=message.message_id,
        )
        await message.answer('Сообщение отправлено☺️')
    elif message.chat.id == MY_ID:
        try:
            with open(FILENAME, 'a', encoding='utf-8') as file:
                file.write(f'{message.text}\n')
        except FileNotFoundError:
            await message.answer(
                'Файл с сообщениями не найден',
                reply_markup=keyboards.show_messages,
            )
        else:
            await message.answer(
                'Сохранено', reply_markup=keyboards.show_messages,
            )


async def main():
    check_necessary_env_vars()
    await asyncio.gather(wish_good_morning(), dispatcher.start_polling(bot))


if __name__ == '__main__':
    asyncio.run(main())
