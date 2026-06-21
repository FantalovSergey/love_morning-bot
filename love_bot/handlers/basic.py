from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .. import config, keyboards
from ..utils import safe_send_message


basic_router = Router()


@basic_router.message(Command("start"))
async def start(request: Message, state: FSMContext):
    """
    Ответ на команду /start.\n
    Можно использовать для сброса FSM.
    """
    await state.clear()
    if request.chat.id == config.MY_ID:
        await request.answer('🖐️', reply_markup=keyboards.my_keyboard)
        return
    await safe_send_message(
        config.ARINA_ID,
        config.START_MESSAGE,
        request.message_id,
        keyboards.Arina_keyboard,
    )


@basic_router.message(F.text == keyboards.CANCEL)
async def cancel(request: Message, state: FSMContext):
    """Отмена ранее выбранного действия."""
    await state.clear()
    await safe_send_message(
        request.chat.id,
        'Есть "Отмена"🫡',
        request.message_id,
        (
            keyboards.Arina_keyboard if request.chat.id == config.ARINA_ID else
            keyboards.my_keyboard
        ),
    )
