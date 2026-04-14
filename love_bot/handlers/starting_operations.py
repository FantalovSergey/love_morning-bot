from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .. import config, fsm, keyboards
from ..content import get_content_from_file, show_content
from ..utils import safe_send_message


starting_operations_router = Router()


@starting_operations_router.message(
    F.text == keyboards.WRITE_DREAM, F.chat.id == config.ARINA_ID,
)
async def start_dream_writing(message: Message, state: FSMContext):
    """Ответ на нажатие Ариной кнопки 'Записать сон📝'."""
    await safe_send_message(
        config.ARINA_ID,
        'Напишите, каким сладеньким сном Вы хотите поделиться😋',
        keyboards.cancel,
        request_message_id=message.message_id,
    )
    await state.set_state(fsm.WriteDream.dream)


@starting_operations_router.message(F.text == keyboards.DELETE_MESSAGES)
async def start_love_messages_deleting(message: Message, state: FSMContext):
    """
    Ответ на нажатие кнопки 'Удалить сообщения'.\n
    Мне – возможность ввода индексов, Арине – предупреждение.
    """
    if message.chat.id == config.ARINA_ID:
        await safe_send_message(
            config.ARINA_ID,
            'Вы делаете что-то очень незаконное🤔🤔🤔',
            request_message_id=message.message_id,
        )
        return
    await show_content(
        message, get_content_from_file(config.LOVE_MESSAGES_FILEPATH),
    )
    await message.answer(
        (
            'Введите диапазоны сообщений через запятую\n'
            'Пример: 1, 17-19, 23-24'
        ),
        reply_markup=keyboards.cancel,
    )
    await state.set_state(fsm.DeleteLoveMessages.indexes)


@starting_operations_router.message(
    F.text == keyboards.DELETE_DREAMES, F.chat.id == config.ARINA_ID,
)
async def start_dreams_deleting(message: Message, state: FSMContext):
    """
    Ответ на нажатие Ариной кнопки 'Удалить нехорошие сны🗑️'.\n
    Появляется возможность ввода индексов.
    """
    await show_content(
        message, get_content_from_file(config.DREAMS_FILEPATH),
    )
    await safe_send_message(
        config.ARINA_ID,
        (
            'Фто тут нувно удалить? Мне нувны номера\n'
            'Например: 1, 17-19, 23-24 кнопочка "Отправить"⏎'
        ),
        keyboards.cancel,
    )
    await state.set_state(fsm.DeleteDreams.indexes)


@starting_operations_router.message(
    F.text == keyboards.WRITE_AS_BOT, F.chat.id == config.MY_ID,
)
async def start_writing_as_bot(message: Message, state: FSMContext):
    """Ответ на нажатие мною кнопки 'Написать от лица бота'."""
    await message.answer('Можно вещать', reply_markup=keyboards.cancel)
    await state.set_state(fsm.SendNoteForArina.note)
