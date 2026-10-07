"""Работа с любовными сообщениями и снами в распоряжении бота."""
import asyncio
from datetime import datetime
from random import choice

from love_bot.core import config
from love_bot.core.exceptions import EmptyFileError, NoContentForDeletingError
from love_bot.core.utils import (
    get_content_for_repr,
    get_date_with_month_written_by_letters,
    get_indexes,
    safe_send_message,
)
from love_bot.files import safe_read_file, safe_write_in_file


def retrieve_content(filepath: str) -> str:
    """
    Вовзращает один элемент контента либо извинения,
    если есть проблемы с файлом.
    """
    try:
        return choice(safe_read_file(filepath))
    except (EmptyFileError, OSError):
        return (
            'Я не могу тебе ничего отправить😢\n'
            'Прости, пожалуйста🙏'
        )


def list_content(filepath: str) -> list[str]:
    """
    Возвращает контент в формате, подходящем для отправки в Telegram:
    с нумерацией и с учётом лимита символов для одного сообщения.\n
    Бросает исключения: EmptyFileError; OSError при ошибках чтения файла.
    """
    return get_content_for_repr(safe_read_file(filepath))


def write_content(filepath: str, text: str, timestamp: bool = False) -> None:
    """
    Запись контента в файл.\n
    В конце файла ставится символ переноса строки.
    Если timestamp=True, указываются дата и время добавления.
    Бросает исключения: OSError при ошибках записи в файл.
    """
    line = [text.replace('\n', ' ')]
    if timestamp:
        now = datetime.now(config.TZ)
        created_at = get_date_with_month_written_by_letters(
            now.strftime('%d.%m.%Y г. %H:%M'),
        )
        line.append(f'Добавлен: {created_at}')
    safe_write_in_file(filepath, 'a', (' '.join(line) + '\n',))


def delete_content(filepath: str, index_ranges: str) -> list[str]:
    """
    Удаление контента из файлов по индексам.\n
    Бросает исключения: EmptyFileError; NoContentForDeletingError;
    OSError при ошибках операций чтения/записи с файлом;
    ValueError при некорректном вводе индексов.\n
    Возвращает удалённый контент в формате, подходящем для отправки в Telegram:
    с нумерацией и с учётом лимита символов для одного сообщения.
    """
    indexes_for_deleting = get_indexes(index_ranges)
    undeleted_content: list[str] = []
    deleted_content: list[str] = []
    content = safe_read_file(filepath)
    for index, line in enumerate(content, start=1):
        if index in indexes_for_deleting:
            deleted_content.append(line)
        else:
            undeleted_content.append(line)
    if not deleted_content:
        ERROR_MESSAGE = (
            'Ошибка удаления контента. '
            'По указанным индексам невозможно удалить ни один элемент'
        )
        asyncio.create_task(safe_send_message(config.MY_ID, ERROR_MESSAGE))
        raise NoContentForDeletingError(ERROR_MESSAGE)
    safe_write_in_file(filepath, 'w', undeleted_content)
    return get_content_for_repr(deleted_content)
