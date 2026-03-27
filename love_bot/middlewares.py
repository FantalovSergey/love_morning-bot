from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class AccessMiddleware(BaseMiddleware):
    def __init__(self, allowed_users: tuple[int]):
        super().__init__()
        self.allowed_users = allowed_users

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if event.message.chat.id not in self.allowed_users:
            await event.message.answer(
                'Доброго времени суток! Этот бот предназначен исключительно '
                'для одного человека, для Арины Атаманюк. Если Вы её знаете, '
                'передайте ей привет🖐️'
            )
            return
        return await handler(event, data)
