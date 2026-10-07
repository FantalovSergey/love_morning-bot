import asyncio

from love_bot.core import config
from love_bot.core.exceptions import (
    EmptyRequestError, TooLongContentMessageError,
)
from love_bot.core.utils import safe_send_message


def validate_request_text_is_not_none(request_text: str | None) -> str:
    """
    Возвращает текст запроса, если он не None,
    иначе бросает EmptyRequestError и логирует это исключение.
    """
    if request_text is None:
        error_message = 'В запросе отсутствует текст'
        asyncio.create_task(safe_send_message(config.MY_ID, error_message))
        raise EmptyRequestError(error_message)
    return request_text


def validate_writing_request(request_text: str | None) -> str:
    """
    Возвращает текст запроса на запись контента, если он валиден,
    иначе бросает EmptyRequestError либо TooLongContentMessageError,
    которое логируется внутри настоящей функции.
    """
    request_text = validate_request_text_is_not_none(request_text)
    symbol_exceeding = len(request_text) - config.WRITING_CONTENT_SYMBOL_LIMIT
    if symbol_exceeding > 0:
        long_message_error = TooLongContentMessageError(
            'Слишком длинное сообщение с контентом для записи в файл',
            symbol_limit_exceeding=symbol_exceeding,
        )
        asyncio.create_task(
            safe_send_message(config.MY_ID, str(long_message_error)),
        )
        raise long_message_error
    return request_text
