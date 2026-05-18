import os

from dotenv import load_dotenv


def get_env_vars() -> tuple[str, int, int]:
    """
    Возвращает кортеж с обязательными переменными окружения.\n
    Порядок следующий: BOT_TOKEN, ARINA_ID, MY_ID.
    Бросает ValueError при отсутствии любой из них с сообщением об ошибке.
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
            'Отсутствуют следующие обязательные переменные окружения:\n'
            f"{', '.join(absent_env_vars)}. Бот не запущен."
        )
    return tuple(env_vars.values())
