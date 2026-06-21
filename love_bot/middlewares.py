from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject


class AccessMiddleware(BaseMiddleware):
    """Ограничение доступа неизвестных пользователей."""
    def __init__(self, *allowed_users: int):
        super().__init__()
        self.allowed_users = allowed_users

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and (
            event.chat.id not in self.allowed_users
        ):
            await event.answer(
                'Доброго времени суток! Этот бот предназначен исключительно '
                'для одного человека, для Арины Атаманюк. Если Вы её знаете, '
                'передайте ей привет🖐️'
            )
            return
        return await handler(event, data)
