from aiogram import F
from aiogram.fsm.context import FSMContext

from love_bot.core import config, keyboards, states, templates
from love_bot.core.utils import safe_send_message
from love_bot.handlers.routers import operations_launching_router


@operations_launching_router.message(
    F.text == keyboards.WRITE_AS_BOT, F.chat.id == config.MY_ID,
)
async def start_writing_as_bot(_, state: FSMContext) -> None:
    """Ответ на нажатие мною кнопки 'Написать от лица бота'."""
    await state.set_state(states.NoteForArinaSending.note_waiting)
    await safe_send_message(
        config.MY_ID,
        templates.WRITING_AS_BOT_INVITE,
        keyboard=keyboards.cancel,
    )
