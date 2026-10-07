from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from love_bot.core import templates
from love_bot.core.utils import safe_send_message


class AccessMiddleware(BaseMiddleware):
    """Ограничение доступа неизвестных пользователей."""
    def __init__(self, *allowed_users: int) -> None:
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
            await safe_send_message(
                event.chat.id,
                templates.MESSAGE_FOR_UNKNOWN_USERS,
                event.message_id,
            )
            return
        return await handler(event, data)
