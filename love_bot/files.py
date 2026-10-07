import asyncio
import errno
from typing import Iterable

from love_bot.core import config
from love_bot.core.exceptions import EmptyFileError
from love_bot.core.utils import safe_send_message

RETRYABLE_EXEPTIONS: tuple[int, ...] = (errno.ESTALE,)


def safe_read_file(filepath: str) -> list[str]:
    """
    Получение контента из файла.\n
    Бросает EmptyFileError при отсустствии содержимого
    или OSError при прочих ошибках, а также логирует их.
    """
    for attempt in range(config.FILE_OPENING_ATTEMPTS_LIMIT):
        try:
            with open(filepath, encoding='utf-8') as file:
                content = file.readlines()
        except FileNotFoundError:
            asyncio.create_task(
                safe_send_message(
                    config.MY_ID, f'Ошибка чтения: файл {filepath} не найден',
                ),
            )
            raise
        except OSError as error:
            issue_message = (
                f'Ошибка "{error.strerror}" при чтении файла {filepath}'
            )
            if (
                error.errno not in RETRYABLE_EXEPTIONS
                or attempt + 1 >= config.FILE_OPENING_ATTEMPTS_LIMIT
            ):
                config.logger.exception(issue_message)
                asyncio.create_task(
                    safe_send_message(config.MY_ID, issue_message),
                )
                raise
            config.logger.warning(
                'Попытка %d/%d\n%s',
                attempt + 1,
                config.FILE_OPENING_ATTEMPTS_LIMIT,
                issue_message,
            )
    if not content:
        error_message = f'Файл {filepath} пуст'
        asyncio.create_task(safe_send_message(config.MY_ID, error_message))
        raise EmptyFileError(error_message)
    return content


def safe_write_in_file(
    filepath: str, mode: str, content: Iterable[str],
) -> None:
    """
    Запись контента в файл.\n
    Бросает OSError при ошибках записи и логирует эти исключения.
    """
    for attempt in range(config.FILE_OPENING_ATTEMPTS_LIMIT):
        try:
            with open(filepath, mode, encoding='utf-8') as file:
                file.writelines(content)
        except FileNotFoundError:
            asyncio.create_task(
                safe_send_message(
                    config.MY_ID,
                    f'Ошибка записи в файл {filepath}. Директория не найдена',
                ),
            )
            raise
        except OSError as error:
            issue_message = (
                f'Ошибка "{error.strerror}" при записи в файл {filepath}'
            )
            if (
                error.errno not in RETRYABLE_EXEPTIONS
                or attempt + 1 >= config.FILE_OPENING_ATTEMPTS_LIMIT
            ):
                config.logger.exception(issue_message)
                asyncio.create_task(
                    safe_send_message(config.MY_ID, issue_message),
                )
                raise
            config.logger.warning(
                'Попытка %d/%d\n%s',
                attempt + 1,
                config.FILE_OPENING_ATTEMPTS_LIMIT,
                issue_message,
            )
