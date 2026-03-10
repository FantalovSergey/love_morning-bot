from aiogram.fsm.state import State, StatesGroup


class DeleteMessages(StatesGroup):
    """FSM для удаления сообщений из файла по индексам."""
    indexes = State()
