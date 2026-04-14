from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .. import config, fsm
from ..content import delete_content, write_content
from ..keyboards import Arina_keyboard, my_keyboard
from ..utils import safe_send_message


fsm_router = Router()


@fsm_router.message(fsm.WriteDream.dream)
async def write_dream(message: Message, state: FSMContext):
    """
    Получение сна из сообщения и запись в файл.\n
    Присутствует ограничение количества символов.
    """
    symbol_exceeding = len(message.text) - config.TO_BOT_MESSAGE_SYMBOL_LIMIT
    if symbol_exceeding > 0:
        symbol_limit_warning = (
            'Как тут много всего🤯🤯🤯\nЯ могу запомнить сон, в котором максимум '
            f'{config.TO_BOT_MESSAGE_SYMBOL_LIMIT} символов🥺\n'
            f'Сократи, пожалуйста, свой сон на {symbol_exceeding} символов🙏'
        )
        await safe_send_message(
            config.ARINA_ID,
            symbol_limit_warning,
            request_message_id=message.message_id,
        )
        return
    await write_content(message, config.DREAMS_FILEPATH, Arina_keyboard)
    await state.clear()


@fsm_router.message(fsm.DeleteLoveMessages.indexes)
async def delete_love_messages(message: Message, state: FSMContext):
    """
    Удаление любовных сообщений из файла по указанным индексам.
    """
    await delete_content(
        message, state, config.LOVE_MESSAGES_FILEPATH, my_keyboard,
    )


@fsm_router.message(fsm.DeleteDreams.indexes)
async def delete_dreams(message: Message, state: FSMContext):
    """
    Удаление снов из файла по указанным индексам.
    """
    await delete_content(
        message, state, config.DREAMS_FILEPATH, Arina_keyboard,
    )


@fsm_router.message(fsm.SendNoteForArina.note)
async def write_note_for_Arina(message: Message, state: FSMContext):
    """Отправка кастомного уведомления из сообщения Арине."""
    await safe_send_message(config.ARINA_ID, message.text)
    await message.answer('✅', reply_markup=my_keyboard)
    await state.clear()
