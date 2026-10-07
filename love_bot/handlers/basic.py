from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from love_bot.core import config, keyboards, templates
from love_bot.core.utils import safe_send_message
from love_bot.handlers.routers import basic_router


@basic_router.message(Command('start'))
async def start(request: Message, state: FSMContext) -> None:
    """
    Ответ на команду /start.\n
    Можно использовать для сброса FSM.
    """
    await state.clear()
    if request.chat.id == config.MY_ID:
        await safe_send_message(
            config.MY_ID,
            templates.START_FOR_ME,
            keyboard=keyboards.my_keyboard,
        )
        return
    await safe_send_message(
        config.ARINA_ID,
        templates.START_MESSAGE_FOR_ARINA,
        request.message_id,
        keyboards.Arina_keyboard,
    )


@basic_router.message(F.text == keyboards.CANCEL)
async def cancel(request: Message, state: FSMContext) -> None:
    """Отмена запущенной операции."""
    await state.clear()
    await safe_send_message(
        request.chat.id,
        templates.CANCEL_RESPONSE,
        request.message_id,
        (
            keyboards.Arina_keyboard if request.chat.id == config.ARINA_ID else
            keyboards.my_keyboard
        ),
    )
