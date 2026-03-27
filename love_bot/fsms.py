from aiogram.fsm.state import State, StatesGroup


class DeleteLoveMessages(StatesGroup):
    """FSM для удаления любовных сообщений."""
    indexes = State()


class DeleteDreams(StatesGroup):
    """FSM для удаления снов."""
    indexes = State()


class WriteDream(StatesGroup):
    """FSM для записи снов."""
    dream = State()


class SendNoteForArina(StatesGroup):
    """FSM для отправки заметок Арине."""
    note = State()
