import os

from dotenv import load_dotenv


def get_env_vars():
    """
    Возвращает кортеж с обязательными переменными окружения.\n
    Порядок следующий: BOT_TOKEN, ARINA_ID, MY_ID.
    Бросает ValueError при отсутствии любой из них с сообщением об ошибке.
    """
    load_dotenv()
    env_vars_keys = ('BOT_TOKEN', 'ARINA_ID', 'MY_ID')
    env_vars = (
        os.getenv('BOT_TOKEN', ''),
        int(os.getenv('ARINA_ID', '0')),
        int(os.getenv('MY_ID', '0')),
    )
    absent_env_vars = [
        env_vars_keys[index] for index, var in enumerate(env_vars) if not var
    ]
    if absent_env_vars:
        raise ValueError(
            'Отсутствуют следующие обязательные переменные окружения:\n'
            f"{', '.join(absent_env_vars)}. Бот не запущен."
        )
    return env_vars
