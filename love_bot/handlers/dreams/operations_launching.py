from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from love_bot.content import list_content
from love_bot.core import config, keyboards, templates
from love_bot.core.exceptions import EmptyFileError
from love_bot.core.states import DreamsDeleting, DreamWriting
from love_bot.core.utils import safe_send_message
from love_bot.handlers.routers import operations_launching_router
from love_bot.tasks import delete_messages_after_content_showing


@operations_launching_router.message(F.text == keyboards.SHOW_DREAMS)
async def show_all_dreams(request: Message) -> None:
    """
    Ответ на нажатие кнопки 'Посмотреть сны'.\n
    По прошествии определённого времени отправленные сообщения исчезают.
    """
    if request.chat.id == config.ARINA_ID:
        await config.bot.forward_message(
            chat_id=config.MY_ID,
            from_chat_id=config.ARINA_ID,
            message_id=request.message_id,
        )
    try:
        messages = list_content(config.DREAMS_FILEPATH)
    except EmptyFileError:
        if request.chat.id == config.ARINA_ID:
            await safe_send_message(config.ARINA_ID, templates.FILE_IS_EMPTY)
        raise
    except OSError:
        if request.chat.id == config.ARINA_ID:
            await safe_send_message(
                config.ARINA_ID, templates.DREAMS_FILE_ERROR,
            )
        raise
    message_ids: list[int] = []
    for message in messages:
        message_id = await safe_send_message(request.chat.id, message)
        if message_id is None:
            break
        message_ids.append(message_id)
    await delete_messages_after_content_showing(request.chat.id, message_ids)


@operations_launching_router.message(
    F.text == keyboards.WRITE_DREAM, F.chat.id == config.ARINA_ID,
)
async def start_dream_writing(request: Message, state: FSMContext) -> None:
    """Ответ на нажатие Ариной кнопки 'Записать сон'."""
    await state.set_state(DreamWriting.dream_waiting)
    await safe_send_message(
        config.ARINA_ID,
        templates.DREAM_WRITING_INVITE,
        request.message_id,
        keyboards.cancel,
    )


@operations_launching_router.message(
    F.text == keyboards.DELETE_DREAMES, F.chat.id == config.ARINA_ID,
)
async def start_dreams_deleting(request: Message, state: FSMContext) -> None:
    """
    Ответ на нажатие Ариной кнопки 'Удалить нехорошие сны'.\n
    Появляется возможность ввода индексов.
    Показываются все сны с индексами,
    которые по прошествии определённого времени исчезают.
    """
    await config.bot.forward_message(
        chat_id=config.MY_ID,
        from_chat_id=config.ARINA_ID,
        message_id=request.message_id,
    )
    try:
        messages = list_content(config.DREAMS_FILEPATH)
    except EmptyFileError:
        await safe_send_message(config.ARINA_ID, templates.NOTHING_TO_DELETE)
        raise
    except OSError:
        await safe_send_message(config.ARINA_ID, templates.DREAMS_FILE_ERROR)
        raise
    message_ids: list[int] = []
    for message in messages:
        message_id = await safe_send_message(config.ARINA_ID, message)
        if message_id is None:
            break
        message_ids.append(message_id)
    else:
        await state.set_state(DreamsDeleting.indexes_waiting)
        await safe_send_message(
            config.ARINA_ID,
            templates.DREAMS_DELETING_INVITE,
            keyboard=keyboards.cancel,
        )
    await delete_messages_after_content_showing(config.ARINA_ID, message_ids)
