import os
from typing import TypedDict

from dotenv import load_dotenv

BOT_IS_NOT_WORKING = 'Бот не запущен'


class EnvVars(TypedDict):
    """Словарь переменных окружения."""
    BOT_TOKEN: str
    ARINA_ID: int
    MY_ID: int


def validate_all_env_vars_are_present(env_vars: EnvVars) -> None:
    """
    Бросает ValueError, если хотя бы одна
    обязательная переменная окружения отсутствует.
    """
    absent_env_vars = [key for key, value in env_vars.items() if not value]
    if absent_env_vars:
        raise ValueError(
            (
                'Отсутствуют следующие обязательные переменные окружения:\n'
                f'{", ".join(absent_env_vars)}. {BOT_IS_NOT_WORKING}'
            ),
        )


def validate_Arina_and_my_ids_are_not_the_same(env_vars: EnvVars) -> None:
    """Бросает ValueError, если ID Арины и мой ID одинаковы."""
    if env_vars['ARINA_ID'] == env_vars['MY_ID']:
        raise ValueError(
            (
                'ID Арины и мой ID не могут иметь одинаковые значения. '
                f'{BOT_IS_NOT_WORKING}'
            ),
        )


def get_env_vars() -> tuple[str, int, int]:
    """
    Возвращает кортеж с обязательными переменными окружения.\n
    Порядок следующий: 'BOT_TOKEN', 'ARINA_ID', 'MY_ID'.
    Бросает ValueError при отсутствии любой из них
    и при совпадении 'ARINA_ID' и 'MY_ID'.
    """
    load_dotenv()
    env_vars: EnvVars = {
        'BOT_TOKEN': os.getenv('BOT_TOKEN', ''),
        'ARINA_ID': int(os.getenv('ARINA_ID', '0')),
        'MY_ID': int(os.getenv('MY_ID', '0')),
    }
    validate_all_env_vars_are_present(env_vars)
    validate_Arina_and_my_ids_are_not_the_same(env_vars)
    return env_vars['BOT_TOKEN'], env_vars['ARINA_ID'], env_vars['MY_ID']
