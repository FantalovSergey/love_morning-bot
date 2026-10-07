from aiogram import F
from aiogram.types import Message

from love_bot.core import config, templates
from love_bot.core.utils import safe_send_message
from love_bot.handlers.routers import simple_messages_router


@simple_messages_router.message(F.chat.id == config.ARINA_ID)
async def handle_Arina_message(request: Message) -> None:
    """Полученное от Арины сообщение пересылается мне."""
    await safe_send_message(
        config.ARINA_ID, templates.SUCCESSFULL_SENDING, request.message_id,
    )
