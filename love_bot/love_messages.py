from random import choice

from aiogram.types import ReplyKeyboardMarkup

from . import config
from .utils import safe_send_message


async def get_messages_from_file() -> list[str] | None:
    """
    Получения всех сообщений из файла.\n
    Логирование ошибок отсутствия самого файла или его содержимого.
    """
    file_error = None
    try:
        with open(config.FILEPATH, encoding='utf-8') as file:
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
            config.logger.error(file_error)
            await safe_send_message(config.MY_ID, file_error)


async def send_love_message():
    """
    Отправка сообщения Арине.\n
    Если есть проблемы с файлом, бот извиняется.
    """
    love_messages = await get_messages_from_file()
    if not love_messages:
        await safe_send_message(
            config.ARINA_ID,
            (
                'Я не могу тебе ничего отправить😢\n'
                'Прости, пожалуйста🙏\n'
                'Я написал Серёже, он попробует всё починить'
            ),
        )
    else:
        await safe_send_message(config.ARINA_ID, choice(love_messages))


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
            if symbol_count > config.BOT_MESSAGE_SYMBOL_LIMIT:
                symbol_count = 0
                await config.bot.send_message(config.MY_ID, ''.join(chunk))
                chunk = []
            chunk.append(f'{index}. {message}')
    else:
        chunk = ['Нет сообщений для просмотра']
    await config.bot.send_message(
        config.MY_ID, ''.join(chunk), reply_markup=keyboard,
    )
