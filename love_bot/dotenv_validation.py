import os
from typing import Dict

from dotenv import load_dotenv


def check_necessary_env_vars() -> Dict | None:
    """
    Возвращает словарь с обязательными переменными окружения.\n
    Бросает ValueError при отсутствии любой из них.
    """
    load_dotenv()
    env_vars = {
        'BOT_TOKEN': os.getenv('BOT_TOKEN'),
        'ARINA_ID': int(os.getenv('ARINA_ID', '0')),
        'MY_ID': int(os.getenv('MY_ID', '0')),
    }
    absent_env_vars = [key for key, var in env_vars.items() if not var]
    if absent_env_vars:
        raise ValueError(
            'Отсутствуют следующие обязательные переменные окружения: '
            f'"{', '.join(absent_env_vars)}". Бот остановлен.'
        )
    return env_vars
