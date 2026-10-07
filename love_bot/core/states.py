from aiogram.fsm.state import State, StatesGroup


class LoveMessagesDeleting(StatesGroup):
    """FSM для удаления любовных сообщений."""
    indexes_waiting = State()


class DreamsDeleting(StatesGroup):
    """FSM для удаления снов."""
    indexes_waiting = State()


class DreamWriting(StatesGroup):
    """FSM для записи снов."""
    dream_waiting = State()


class NoteForArinaSending(StatesGroup):
    """FSM для отправки заметок Арине."""
    note_waiting = State()
