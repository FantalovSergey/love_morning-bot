from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from love_bot.core import config, keyboards, states, templates
from love_bot.core.utils import safe_send_message
from love_bot.handlers.routers import fsm_router


@fsm_router.message(states.NoteForArinaSending.note_waiting)
async def write_note_for_Arina(request: Message, state: FSMContext) -> None:
    """Отправка Арине кастомного уведомления из сообщения."""
    await config.bot.copy_message(
        chat_id=config.ARINA_ID,
        from_chat_id=config.MY_ID,
        message_id=request.message_id,
    )
    await state.clear()
    await safe_send_message(
        config.MY_ID, templates.SUCCESS, keyboard=keyboards.my_keyboard,
    )
