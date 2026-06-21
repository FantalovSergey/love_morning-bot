from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .. import config, fsm
from ..content import delete_content, write_content
from ..keyboards import Arina_keyboard, my_keyboard
from ..utils import safe_send_message


fsm_router = Router()


@fsm_router.message(fsm.WriteDream.dream)
async def write_dream(request: Message, state: FSMContext):
    """
    Получение сна из сообщения и запись в файл.\n
    Присутствует ограничение количества символов.
    """
    if request.text is None:
        await safe_send_message(
            config.ARINA_ID,
            'А фто нувно запифать, я не увидел😫😫😫',
            request.message_id,
        )
        return
    symbol_exceeding = len(request.text) - config.TO_BOT_MESSAGE_SYMBOL_LIMIT
    if symbol_exceeding > 0:
        symbol_limit_warning = (
            'Как тут много всего🤯🤯🤯\nЯ могу запомнить сон, в котором максимум '
            f'{config.TO_BOT_MESSAGE_SYMBOL_LIMIT} символов🥺\n'
            f'Сократи, пожалуйста, свой сон на {symbol_exceeding} символов🙏'
        )
        await safe_send_message(
            config.ARINA_ID, symbol_limit_warning, request.message_id,
        )
        return
    await state.clear()
    await write_content(request, config.DREAMS_FILEPATH, Arina_keyboard)


@fsm_router.message(fsm.DeleteLoveMessages.indexes)
async def delete_love_messages(request: Message, state: FSMContext):
    """
    Удаление любовных сообщений из файла по указанным индексам.
    """
    await delete_content(
        request, state, config.LOVE_MESSAGES_FILEPATH, my_keyboard,
    )


@fsm_router.message(fsm.DeleteDreams.indexes)
async def delete_dreams(request: Message, state: FSMContext):
    """Удаление снов из файла по указанным индексам."""
    await delete_content(
        request, state, config.DREAMS_FILEPATH, Arina_keyboard,
    )


@fsm_router.message(fsm.SendNoteForArina.note)
async def write_note_for_Arina(request: Message, state: FSMContext):
    """Отправка Арине кастомного уведомления из сообщения."""
    await state.clear()
    await config.bot.copy_message(
        config.ARINA_ID,
        config.MY_ID,
        request.message_id,
    )
    await request.answer('✅', reply_markup=my_keyboard)
