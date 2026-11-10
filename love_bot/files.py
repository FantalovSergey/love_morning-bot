import asyncio
import errno
from typing import Sequence

from love_bot.core import config
from love_bot.core.exceptions import EmptyFileError
from love_bot.core.utils import telegram_logging

RETRYABLE_EXEPTIONS: tuple[int, ...] = (errno.ESTALE,)


async def safe_read_file(filepath: str) -> list[str]:
    """
    Получение контента из файла.\n
    Бросает EmptyFileError при отсустствии содержимого
    или OSError при прочих ошибках, а также логирует их.
    """
    for attempt in range(config.OPENING_ATTEMPTS_LIMIT):
        try:
            with open(filepath, encoding='utf-8') as file:
                content = file.readlines()
                break
        except FileNotFoundError:
            telegram_logging(f'Ошибка чтения: файл {filepath} не найден')
            raise
        except OSError as error:
            issue_message = (
                f'Ошибка "{error.strerror}" при чтении файла {filepath}'
            )
            if (
                error.errno not in RETRYABLE_EXEPTIONS
                or attempt + 1 >= config.OPENING_ATTEMPTS_LIMIT
            ):
                config.logger.exception(issue_message)
                telegram_logging(issue_message)
                raise
            config.logger.warning(
                'Попытка %d/%d\n%s',
                attempt + 1,
                config.OPENING_ATTEMPTS_LIMIT,
                issue_message,
            )
            await asyncio.sleep(config.REOPENING_PERIOD)
    if not content:
        error_message = f'Файл {filepath} пуст'
        telegram_logging(error_message)
        raise EmptyFileError(error_message)
    return content


async def safe_write_in_file(
    filepath: str, mode: str, content: Sequence[str],
) -> None:
    """
    Запись контента в файл.\n
    Бросает OSError при ошибках записи и логирует эти исключения.
    """
    for attempt in range(config.OPENING_ATTEMPTS_LIMIT):
        try:
            with open(filepath, mode, encoding='utf-8') as file:
                return file.writelines(content)
        except FileNotFoundError:
            telegram_logging(
                f'Ошибка записи в файл {filepath}. Директория не найдена',
            )
            raise
        except OSError as error:
            issue_message = (
                f'Ошибка "{error.strerror}" при записи в файл {filepath}'
            )
            if (
                error.errno not in RETRYABLE_EXEPTIONS
                or attempt + 1 >= config.OPENING_ATTEMPTS_LIMIT
            ):
                config.logger.exception(issue_message)
                telegram_logging(issue_message)
                raise
            config.logger.warning(
                'Попытка %d/%d\n%s',
                attempt + 1,
                config.OPENING_ATTEMPTS_LIMIT,
                issue_message,
            )
            await asyncio.sleep(config.REOPENING_PERIOD)
