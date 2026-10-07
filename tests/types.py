from typing import Awaitable, Protocol

from aiogram import Dispatcher
from aiogram.fsm.state import State
from aiogram.types import Update


class DispatcherFactory(Protocol):
    def __call__(
        self, chat_id: int, state: State = State('test'),
    ) -> Awaitable[Dispatcher]:
        pass


class UpdateFactory(Protocol):
    def __call__(self, chat_id: int = 1, text_message: str = 'test') -> Update:
        pass
