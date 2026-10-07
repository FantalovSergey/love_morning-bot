from aiogram import F
from aiogram.types import Message

from love_bot.content import write_content
from love_bot.core import config, templates
from love_bot.core.utils import safe_send_message
from love_bot.handlers.routers import simple_messages_router
from love_bot.validators import validate_writing_request


@simple_messages_router.message(F.chat.id == config.MY_ID)
async def write_love_message(request: Message) -> None:
    """Запись любовного сообщения в файл."""
    write_content(
        config.LOVE_MESSAGES_FILEPATH, validate_writing_request(request.text),
    )
    await safe_send_message(config.MY_ID, templates.CONTENT_IS_SAVED)
