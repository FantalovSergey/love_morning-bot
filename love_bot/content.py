"""Работа с любовными сообщениями и снами в распоряжении бота."""
import asyncio
from datetime import datetime
from random import choice

from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext

from . import config
from .utils import (
    get_indexes, get_date_with_month_written_by_letters, safe_send_message,
)


async def wish_good_morning():
    """Пожелание доброго утра каждый день в определённое время."""
    while True:
        now = datetime.now(config.TZ)
        delta = now.replace(**config.SENDING_TIME) - now
        # Если дельта отрицательная, свойство seconds вернёт количество секунд
        # до момента отправки, которая произойдёт на следующий день
        await asyncio.sleep(delta.seconds)
        await send_love_message()
        await asyncio.sleep(1)


def get_content_from_file(filepath: str) -> list[str]:
    """
    Получения всех любовных сообщений или снов из файлов.\n
    Логирование ошибок отсутствия самого файла
    или содержимого файла с любовными сообщениями.
    """
    try:
        with open(filepath, encoding='utf-8') as file:
            content = file.readlines()
    except FileNotFoundError:
        config.logger.error(f'Файл {filepath} не найден.')
        return []
    if not content and filepath == config.LOVE_MESSAGES_FILEPATH:
        config.logger.error(f'Файл {filepath} пуст.')
    return content


async def send_love_message(request_message_id: int | None = None):
    """
    Отправка любовного сообщения Арине.\n
    Если есть проблемы с файлом, бот извиняется.
    """
    love_messages = get_content_from_file(config.LOVE_MESSAGES_FILEPATH)
    if not love_messages:
        await safe_send_message(
            config.ARINA_ID,
            (
                'Я не могу тебе ничего отправить😢\n'
                'Прости, пожалуйста🙏\n'
                'Я написал Серёже, он попробует всё починить'
            ),
            request_message_id=request_message_id,
        )
        return
    love_message = choice(love_messages)
    now = datetime.now(config.TZ)
    for hour_range, hello_phrase in config.DAY_PARTS_EXCEPT_MORNING:
        if now.hour in hour_range:
            love_message = love_message.replace('Доброе утро', hello_phrase)
            break
    await safe_send_message(
        config.ARINA_ID, love_message, request_message_id=request_message_id,
    )


async def write_content(
    request: Message,
    filepath: str,
    keyboard: ReplyKeyboardMarkup | None = None,
):
    """
    Запись любовных сообщений или снов в файлы.\n
    У снов указываются дата и время добавления.
    """
    with open(filepath, 'a', encoding='utf-8') as file:
        line = [request.text.replace('\n', ' ')]
        if request.chat.id == config.ARINA_ID:
            now = datetime.now(config.TZ)
            created_at = get_date_with_month_written_by_letters(
                now.strftime('%d.%m.%Y г. %H:%M')
            )
            line.append(f'Добавлен: {created_at}')
        file.writelines((' '.join(line) + '\n',))
    await safe_send_message(
        request.chat.id, 'Сохранено☺️', keyboard, request.message_id,
    )


async def show_content(request: Message, content: list[str]) -> list[Message]:
    """
    Отправка исчезающих любовных сообщений или снов в л/с по запросу.\n
    Учитывается лимит символов Telegram для одного сообщения.
    Содержимое (любовные сообщения или сны) пронумеровано.
    Если контент запрашивает Арина, запрос пересылается мне сразу и 1 раз.\n
    Возвращает список отправленных сообщений с контентом.
    """
    if request.chat.id == config.ARINA_ID:
        await config.bot.forward_message(
            chat_id=config.MY_ID,
            from_chat_id=config.ARINA_ID,
            message_id=request.message_id,
        )
    messages = []
    if not content:
        chunk = ['Пуфто, ничего нет🙃']
    else:
        chunk = []
        symbol_count = 0
        for index, line in enumerate(content, start=1):
            line_length = len(line)
            if symbol_count + line_length > (
                config.FROM_BOT_MESSAGE_SYMBOL_LIMIT
            ):
                messages.append(
                    await safe_send_message(request.chat.id, ''.join(chunk))
                )
                chunk = []
                symbol_count = 0
            chunk.append(f'{index}. {line}')
            symbol_count += line_length
    messages.append(await safe_send_message(request.chat.id, ''.join(chunk)))
    return messages


async def delete_content(
    request: Message,
    state: FSMContext,
    filepath: str,
    keyboard: ReplyKeyboardMarkup,
):
    """Удаление любовных сообщений или снов из файлов по индексам."""
    try:
        indexes_for_deleting = get_indexes(request.text)
    except ValueError:
        await safe_send_message(
            request.chat.id,
            'Проверьте правильность ввода😐',
            request_message_id=request.message_id,
        )
        return
    await state.clear()
    undeleted_content = []
    deleted_content = []
    for index, line in enumerate(get_content_from_file(filepath), start=1):
        (
            deleted_content.append(line) if index in indexes_for_deleting else
            undeleted_content.append(line)
        )
    with open(filepath, 'w', encoding='utf-8') as file:
        file.writelines(undeleted_content)
    await show_content(request, deleted_content)
    await safe_send_message(request.chat.id, 'Я удалив вот это👆🤙💫', keyboard)
