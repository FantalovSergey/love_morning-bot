import asyncio

from aiogram.exceptions import TelegramNetworkError, TelegramServerError
from aiogram.types import Message, ReplyKeyboardMarkup

from . import config


async def safe_send_message(
    chat_id: int,
    message: str,
    keyboard: ReplyKeyboardMarkup | None = None,
    request_message_id: int | None = None,
) -> int:
    """
    Отправка сообщений по указанному id пользователя.\n
    Логирование исключений; 'chat not found' не обрабатывается,
    т.к. бот запускается раньше, чем ссылку на него получает Арина.
    Пересылка мне сообщения бота, отправленного Арине,
    и исходного сообщения Арины при наличии соответствующего аргумента.\n
    Возвращает id отправленного сообщения.
    """
    try:
        sent_message = await config.bot.send_message(
            chat_id, message, reply_markup=keyboard,
        )
    except (TelegramNetworkError, TelegramServerError):
        config.logger.exception('Сбой при отправке сообщения в Telegram.')
    except Exception as error:
        if 'chat not found' not in str(error):
            config.logger.exception(
                'Мы не знаем, что это такое, если бы мы знали, '
                f'что это такое, мы не знаем, что это такое:\n{error}'
            )
    else:
        if chat_id == config.ARINA_ID:
            if request_message_id is not None:
                await config.bot.forward_message(
                    chat_id=config.MY_ID,
                    from_chat_id=config.ARINA_ID,
                    message_id=request_message_id,
                )
            await config.bot.forward_message(
                chat_id=config.MY_ID,
                from_chat_id=config.ARINA_ID,
                message_id=sent_message.message_id,
            )
        return sent_message.message_id


async def delete_messages_after_showing_content(
    chat_id: int, messages: list[Message],
):
    """Удаление сообщений с контентом через некоторое время."""
    await asyncio.sleep(config.CONTENT_SHOWING_PERIOD)
    if len(messages) > 1:
        await config.bot.delete_messages(chat_id, messages[1:])
    await config.bot.edit_message_text(
        'Я показал, а потом удалив, штобы никто не подсмотрел🐻',
        chat_id=chat_id,
        message_id=messages[0],
    )


def get_indexes(text: str) -> list[int]:
    """Преобразование текста с диапазонами сообщений в список индексов."""
    index_ranges = text.split(', ')
    indexes = []
    for index_range in index_ranges:
        if '-' in index_range:
            start_index, stop_index = index_range.split('-')
            for index in range(int(start_index), int(stop_index) + 1):
                indexes.append(index)
        else:
            indexes.append(int(index_range))
    return indexes
