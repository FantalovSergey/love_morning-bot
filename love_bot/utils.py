from aiogram.exceptions import TelegramNetworkError, TelegramServerError
from aiogram.types import ReplyKeyboardMarkup

from . import config


async def safe_send_message(
    chat_id: int,
    message: str,
    keyboard: ReplyKeyboardMarkup | None = None,
    request_message_id: int | None = None,
):
    """
    Отправка сообщений по указанному id пользователя.\n
    Пересылка сообщения бота, отправленного Арине,
    и по необходимости исходного сообщения Арины.
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
