from aiogram.fsm.state import State, StatesGroup


class DeleteMessages(StatesGroup):
    indexes = State()
