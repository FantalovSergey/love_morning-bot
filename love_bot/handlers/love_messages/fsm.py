from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from love_bot.content import delete_content
from love_bot.core import config, states, templates
from love_bot.core.keyboards import my_keyboard
from love_bot.core.utils import safe_send_message
from love_bot.handlers.routers import fsm_router
from love_bot.validators import validate_request_text_is_not_none


@fsm_router.message(states.LoveMessagesDeleting.indexes_waiting)
async def delete_love_messages(request: Message, state: FSMContext) -> None:
    """
    Удаление любовных сообщений из файла по указанным индексам.
    """
    deleted_love_messages = delete_content(
        config.LOVE_MESSAGES_FILEPATH,
        validate_request_text_is_not_none(request.text),
    )
    await state.clear()
    for message in deleted_love_messages:
        if await safe_send_message(config.MY_ID, message) is None:
            break
    else:
        await safe_send_message(
            config.MY_ID, templates.CONTENT_IS_DELETED, keyboard=my_keyboard,
        )
