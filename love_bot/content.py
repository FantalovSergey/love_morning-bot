"""Работа с любовными сообщениями и снами в распоряжении бота."""
from datetime import datetime
from random import choice

from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext

from . import config
from .utils import get_indexes, safe_send_message


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
    Отправка сообщения Арине.\n
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
    """Запись любовных сообщений и снов в файлы."""
    with open(filepath, 'a', encoding='utf-8') as file:
        file.writelines((f'{request.text.replace('\n', ' ')}\n',))
    await safe_send_message(
        request.chat.id, 'Сохранено☺️', keyboard, request.message_id,
    )


async def show_content(request: Message, content: list[str]):
    """
    Отправляет любовные сообщения или сны в л/с по запросу.\n
    Учитывается лимит символов Telegram для одного сообщения.
    Содержимое (любовные сообщения или сны) пронумеровано.
    """
    if request.chat.id == config.ARINA_ID:
        await config.bot.forward_message(
            chat_id=config.MY_ID,
            from_chat_id=config.ARINA_ID,
            message_id=request.message_id,
        )
    if not content:
        chunk = ['Пуфто, ничего нет🙃']
    else:
        chunk = []
        symbol_count = 0
        for index, line in enumerate(content, start=1):
            symbol_count += len(line)
            if symbol_count > config.FROM_BOT_MESSAGE_SYMBOL_LIMIT:
                symbol_count = 0
                await safe_send_message(request.chat.id, ''.join(chunk))
                chunk = []
            chunk.append(f'{index}. {line}')
    await safe_send_message(request.chat.id, ''.join(chunk))


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
    undeleted_content = []
    deleted_content = []
    for index, line in enumerate(get_content_from_file(filepath), start=1):
        (
            deleted_content.append(line)
            if index in indexes_for_deleting
            else undeleted_content.append(line)
        )
    with open(filepath, 'w', encoding='utf-8') as file:
        file.writelines(undeleted_content)
    await show_content(request, deleted_content)
    await safe_send_message(request.chat.id, 'Я удалив вот это👆🤙💫', keyboard)
    await state.clear()
