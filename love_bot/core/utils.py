import asyncio
from datetime import datetime

from aiogram.exceptions import TelegramNetworkError, TelegramServerError
from aiogram.types import ReplyKeyboardMarkup

from love_bot.core import config


async def safe_send_message(
    chat_id: int,
    message: str,
    request_message_id: int | None = None,
    keyboard: ReplyKeyboardMarkup | None = None,
) -> int | None:
    """
    Отправка сообщений по указанному id пользователя.\n
    Логирование исключений. Пересылка мне сообщения бота, отправленного не мне,
    а также полученного ботом сообщения
    при наличии соответствующего аргумента.\n
    Возвращает id отправленного сообщения.
    """
    error_message = (
        f'Сообщение "{message}" НЕ ОТПРАВЛЕНО '
        f'в чат {chat_id}, request_message_id = {request_message_id}'
    )
    try:
        sent_message = await config.bot.send_message(
            chat_id, message, reply_markup=keyboard,
        )
    except (TelegramNetworkError, TelegramServerError):
        config.logger.exception('%s\n\nTelegram недоступен', error_message)
        return None
    except Exception as error:
        if 'chat not found' in str(error).lower():
            config.logger.exception(
                '%s\n\nЧат с пользователем не найден', error_message,
            )
        else:
            config.logger.exception(
                (
                    '%s\n\nМы не знаем, что это такое, если бы мы знали, '
                    'что это такое, мы не знаем, что это такое:'
                ),
                error_message,
            )
        asyncio.create_task(
            config.bot.send_message(
                config.MY_ID,
                'Ошибка отправки сообщения. Подробнее в лог-файле',
            ),
        )
        return None
    if chat_id != config.MY_ID:
        if request_message_id is not None:
            await config.bot.forward_message(
                chat_id=config.MY_ID,
                from_chat_id=chat_id,
                message_id=request_message_id,
            )
        await config.bot.forward_message(
            chat_id=config.MY_ID,
            from_chat_id=chat_id,
            message_id=sent_message.message_id,
        )
    return sent_message.message_id


def get_indexes(text: str) -> list[int]:
    """
    Преобразование строки с диапазонами в список индексов.\n
    Бросает и логирует ValueError в случае некорректного ввода диапазонов.
    """
    index_ranges = text.split(', ')
    indexes: list[int] = []
    try:
        for index_range in index_ranges:
            if '-' in index_range:
                start_index, stop_index = index_range.split('-')
                for index in range(int(start_index), int(stop_index) + 1):
                    indexes.append(index)
            else:
                indexes.append(int(index_range))
    except ValueError as error:
        asyncio.create_task(safe_send_message(config.MY_ID, str(error)))
        raise
    return indexes


def get_content_for_repr(content: list[str]) -> list[str]:
    """
    Нумерует контент и упаковывает его в сообщения
    с учетом лимита символов Telegram для одного сообщения.
    """
    chunks: list[str] = []
    chunk: list[str] = []
    symbol_count = 0
    for index, line in enumerate(content, start=1):
        line = f'{index}. {line}'
        line_length = len(line)
        if symbol_count + line_length > config.TELEGRAM_MESSAGE_SYMBOL_LIMIT:
            chunks.append(''.join(chunk))
            chunk = []
            symbol_count = 0
        chunk.append(line)
        symbol_count += line_length
    chunks.append(''.join(chunk))
    return chunks


def get_message_with_right_greeting(message: str) -> str:
    """
    Меняет в сообщении 'Доброе утро' на корректную приветственную фразу
    с учётом времени суток.
    """
    now = datetime.now(config.TZ)
    for hour_range, greeting in config.GREETINGS_EXCEPT_MORNING:
        if now.hour in hour_range:
            message = message.replace('Доброе утро', greeting)
            break
    return message


def get_date_with_month_written_by_letters(date: str) -> str:
    """
    Принимает строку с датой в формате '%d.%m'
    (после месяца допускаются любые символы).\n
    Возвращает строку с датой, где месяц записан словом,
    а однозначное число – одной цифрой.
    """
    MONTHS = (
        'января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
        'августа', 'сентября', 'октября', 'ноября', 'декабря',
    )
    day = int(date[:2])
    month = MONTHS[int(date[3:5]) - 1]
    other = date[6:]
    return f'{day} {month} {other}'
