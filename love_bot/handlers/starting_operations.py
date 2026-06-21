from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .. import config, fsm, keyboards
from ..content import get_content_from_file, show_content
from ..utils import delete_messages_after_showing_content, safe_send_message


starting_operations_router = Router()


@starting_operations_router.message(
    F.text == keyboards.WRITE_DREAM, F.chat.id == config.ARINA_ID,
)
async def start_dream_writing(request: Message, state: FSMContext):
    """Ответ на нажатие Ариной кнопки 'Записать сон📝'."""
    await state.set_state(fsm.WriteDream.dream)
    await safe_send_message(
        config.ARINA_ID,
        'Напишите, каким сладеньким сном Вы хотите поделиться😋',
        request.message_id,
        keyboards.cancel,
    )


@starting_operations_router.message(F.text == keyboards.DELETE_MESSAGES)
async def start_love_messages_deleting(request: Message, state: FSMContext):
    """
    Ответ на нажатие кнопки 'Удалить сообщения'.\n
    Мне – возможность ввода индексов, Арине – предупреждение.
    """
    if request.chat.id == config.ARINA_ID:
        await safe_send_message(
            config.ARINA_ID,
            'Вы делаете что-то очень незаконное🤔🤔🤔',
            request.message_id,
        )
        return
    await state.set_state(fsm.DeleteLoveMessages.indexes)
    messages = await show_content(
        request, get_content_from_file(config.LOVE_MESSAGES_FILEPATH),
    )
    await request.answer(
        (
            'Список всех сообщений☝️\n'
            'Введите диапазоны сообщений через запятую\n'
            'Пример: 1, 17-19, 23-24'
        ),
        reply_markup=keyboards.cancel,
    )
    await delete_messages_after_showing_content(config.MY_ID, messages)


@starting_operations_router.message(
    F.text == keyboards.DELETE_DREAMES, F.chat.id == config.ARINA_ID,
)
async def start_dreams_deleting(request: Message, state: FSMContext):
    """
    Ответ на нажатие Ариной кнопки 'Удалить нехорошие сны🗑️'.\n
    Появляется возможность ввода индексов.
    """
    await state.set_state(fsm.DeleteDreams.indexes)
    messages = await show_content(
        request, get_content_from_file(config.DREAMS_FILEPATH),
    )
    await safe_send_message(
        config.ARINA_ID,
        (
            'Воть все Ваши сны☝️\n'
            'Фто тут нувно удалить? Мне нувны номера\n'
            'Например: 1, 17-19, 23-24 кнопочка "Отправить"⏎'
        ),
        keyboard=keyboards.cancel,
    )
    await delete_messages_after_showing_content(config.ARINA_ID, messages)


@starting_operations_router.message(
    F.text == keyboards.WRITE_AS_BOT, F.chat.id == config.MY_ID,
)
async def start_writing_as_bot(request: Message, state: FSMContext):
    """Ответ на нажатие мною кнопки 'Написать от лица бота'."""
    await state.set_state(fsm.SendNoteForArina.note)
    await request.answer('Можно вещать', reply_markup=keyboards.cancel)
