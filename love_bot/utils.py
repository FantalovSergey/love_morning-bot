import asyncio

from aiogram.exceptions import TelegramNetworkError, TelegramServerError

from . import config


async def safe_send_message(chat_id: int, message: str):
    """
    Отправка сообщений по указанному id пользователя.\n
    Повторная отправка при ошибках подключения к Telegram.
    Логирование прочих исключений.
    """
    while True:
        try:
            await config.bot.send_message(chat_id, message)
        except (TelegramNetworkError, TelegramServerError):
            config.logger.exception('Сбой при отправке сообщения в Telegram.')
            await asyncio.sleep(config.RETRY_PERIOD)
        except Exception as error:
            if 'chat not found' not in error:
                config.logger.exception(
                    'Мы не знаем, что это такое, если бы мы знали, '
                    f'что это такое, мы не знаем, что это такое:\n{error}'
                )
        else:
            if chat_id == config.ARINA_ID:
                await config.bot.send_message(
                    config.MY_ID, f'Отправлено:\n{message}',
                )
            break


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
