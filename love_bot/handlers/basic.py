from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .. import config, keyboards
from ..utils import safe_send_message


basic_router = Router()


@basic_router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    """
    Ответ на команду /start.\n
    Можно использовать для сброса FSM.
    """
    await state.clear()
    if message.chat.id == config.MY_ID:
        await message.answer('🖐️', reply_markup=keyboards.my_keyboard)
        return
    await safe_send_message(
        config.ARINA_ID,
        config.START_MESSAGE,
        keyboards.Arina_keyboard,
        request_message_id=message.message_id,
    )


@basic_router.message(F.text == keyboards.CANCEL)
async def cancel(message: Message, state: FSMContext):
    """Отмена ранее выбранного действия."""
    await safe_send_message(
        message.chat.id,
        'Есть "Отмена"🫡',
        (
            keyboards.Arina_keyboard if message.chat.id == config.ARINA_ID else
            keyboards.my_keyboard
        ),
        request_message_id=message.message_id,
    )
    await state.clear()
