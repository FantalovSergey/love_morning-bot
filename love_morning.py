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

format = '%(asctime)s %(levelname)s %(message)s'
handler = RotatingFileHandler('/data/logs.log', maxBytes=500000, backupCount=5)
handler.setFormatter(logging.Formatter(format))
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


def check_necessary_env_vars():
    """
    Проверяет обязательные переменные окружения.\n
    Бот будет остановлен при отсутствии любой из них.
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
    Отправка сообщений по указанному id пользователя.\n
    Повторная отправка при ошибках подключения к Telegram.
    """
    while True:
        try:
            await bot.send_message(chat_id, message)
        except (TelegramNetworkError, TelegramServerError):
            logger.exception('Сбой при отправке сообщения в Telegram.')
            await asyncio.sleep(RETRY_PERIOD)
        except Exception as error:
            if 'chat not found' not in error:
                logger.exception(
                    'Мы не знаем, что это такое, если бы мы знали, '
                    f'что это такое, мы не знаем, что это такое:\n{error}'
                )
        else:
            if chat_id == ARINA_ID:
                await bot.send_message(MY_ID, f'Отправлено:\n{message}')
            break


async def get_messages_from_file() -> list[str] | None:
    """
    Получения всех сообщений из файла.\n
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
    Отправка сообщения Арине.\n
    Если есть проблемы с файлом, бот извиняется.
    """
    love_messages = await get_messages_from_file()
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


async def show_messages(messages: list[str], keyboard: ReplyKeyboardMarkup):
    """
    Отправка списка сообщений вместе с клавиатурой по моему запросу.\n
    Учитывается лимит символов Telegram для одного сообщения.
    """
    if messages:
        chunk = []
        symbol_count = 0
        for index, message in enumerate(messages):
            symbol_count += len(message)
            if symbol_count > BOT_MESSAGE_SYMBOL_LIMIT:
                symbol_count = 0
                await bot.send_message(MY_ID, ''.join(chunk))
                chunk = []
            chunk.append(f'{index}. {message}')
    else:
        chunk = ['Нет сообщений для просмотра']
    await bot.send_message(MY_ID, ''.join(chunk), reply_markup=keyboard)


async def wish_good_morning():
    """Пожелание доброго утра каждый день в определённое время."""
    while True:
        now = datetime.now(TZ)
        delta = now.replace(**SENDING_TIME) - now
        # Если дельта отрицательная, свойство seconds вернёт количество секунд
        # до момента отправки, которая произойдёт на следующий день
        await asyncio.sleep(delta.seconds)
        await send_love_message()
        await asyncio.sleep(1)


@dispatcher.message(Command("start"))
async def start(message: Message):
    """
    Ответ на команду /start.\n
    Неизвестным пользователям отправляется соответствующее сообщение.
    """
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
    elif message.chat.id == MY_ID:
        await message.answer('🖐️', reply_markup=keyboards.show_messages)
    else:
        await message.answer(FOR_UNKNOWN_USERS)


@dispatcher.message(F.text == keyboards.GET_CUTENESS_TEXT)
async def send_cuteness_immediately(message: Message):
    """Ответ на нажатие Ариной кнопки 'Получить милоту райт нау!!'"""
    if message.chat.id == ARINA_ID:
        await send_love_message()


@dispatcher.message(F.text == keyboards.SHOW_MESSAGES_TEXT)
async def show_all_love_messages(message: Message):
    """
    Ответ на нажатие кнопки 'Посмотреть сообщения'.\n
    Мне – все сообщения из файла, Арине – предупреждение.
    """
    if message.chat.id == MY_ID:
        love_messages = await get_messages_from_file()
        if love_messages:
            await show_messages(love_messages, keyboards.delete_messages)
    elif message.chat.id == ARINA_ID:
        await safe_send_message(ARINA_ID, 'Вы делаете что-то незаконное🤔')


@dispatcher.message(F.text == keyboards.DELETE_MESSAGES_TEXT)
async def start_love_messages_deleting(message: Message, state: FSMContext):
    """
    Ответ на нажатие кнопки 'Удалить сообщения'.\n
    Мне – возможность ввода индексов либо отмены удаления нажатием кнопки,
    Арине – предупреждение.
    """
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
    elif message.chat.id == ARINA_ID:
        await safe_send_message(
            ARINA_ID, 'Вы делаете что-то очень незаконное🤔🤔🤔'
        )


@dispatcher.message(DeleteMessages.indexes)
async def delete_love_messages(message: Message, state: FSMContext):
    """
    Удаление сообщений из файла по указанным индексам или отмена удаления.
    """
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
            messages_from_file = await get_messages_from_file()
            if messages_from_file:
                undeleted_messages = []
                deleted_messages = []
                for index, message_from_file in enumerate(messages_from_file):
                    (
                        deleted_messages.append(message_from_file)
                        if index in indexes_for_deleting
                        else undeleted_messages.append(message_from_file)
                    )
                with open(FILENAME, 'w', encoding='utf-8') as file:
                    file.writelines(undeleted_messages)
                await message.answer('Удалены следующие сообщения:')
                await show_messages(deleted_messages, keyboards.show_messages)
                await state.clear()


@dispatcher.message()
async def receive_message(message: Message):
    """Обработка прочих сообщений.\n
    Моё сообщение сохраняется в файл как любовное,
    сообщение Арины пересылается мне.
    """
    if message.chat.id == MY_ID:
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
    elif message.chat.id == ARINA_ID:
        await bot.forward_message(
            chat_id=MY_ID,
            from_chat_id=ARINA_ID,
            message_id=message.message_id,
        )
        await message.answer('Сообщение отправлено☺️')


async def main():
    check_necessary_env_vars()
    await asyncio.gather(wish_good_morning(), dispatcher.start_polling(bot))


if __name__ == '__main__':
    asyncio.run(main())
