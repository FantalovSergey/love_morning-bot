from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from love_bot.content import delete_content, write_content
from love_bot.core import config, states, templates
from love_bot.core.exceptions import (
    EmptyFileError,
    EmptyRequestError,
    NoContentForDeletingError,
    TooLongContentMessageError,
)
from love_bot.core.keyboards import Arina_keyboard
from love_bot.core.utils import safe_send_message
from love_bot.handlers.routers import fsm_router
from love_bot.validators import (
    validate_request_text_is_not_none, validate_writing_request,
)


@fsm_router.message(states.DreamWriting.dream_waiting)
async def write_dream(request: Message, state: FSMContext) -> None:
    """
    Получение сна из сообщения и запись в файл.\n
    Присутствует ограничение количества символов.
    """
    try:
        write_content(
            config.DREAMS_FILEPATH,
            validate_writing_request(request.text),
            timestamp=True,
        )
    except EmptyRequestError:
        await safe_send_message(
            config.ARINA_ID,
            templates.WRITE_DREAM_REQUEST_IS_EMPTY,
            request.message_id,
        )
        raise
    except TooLongContentMessageError as error:
        await safe_send_message(
            config.ARINA_ID,
            templates.get_too_long_dream_warning(error.symbol_limit_exceeding),
            request.message_id,
        )
        raise
    except OSError:
        await safe_send_message(
            config.ARINA_ID, templates.DREAMS_FILE_ERROR, request.message_id,
        )
        raise
    await state.clear()
    await safe_send_message(
        config.ARINA_ID,
        templates.CONTENT_IS_SAVED,
        request.message_id,
        Arina_keyboard,
    )


@fsm_router.message(states.DreamsDeleting.indexes_waiting)
async def delete_dreams(request: Message, state: FSMContext) -> None:
    """Удаление снов из файла по указанным индексам."""
    await config.bot.forward_message(
        chat_id=config.MY_ID,
        from_chat_id=config.ARINA_ID,
        message_id=request.message_id,
    )
    try:
        deleted_dreams = delete_content(
            config.DREAMS_FILEPATH,
            validate_request_text_is_not_none(request.text),
        )
    except NoContentForDeletingError:
        await safe_send_message(
            config.ARINA_ID, templates.OUT_OF_RANGE_INDEXES_ERROR,
        )
        raise
    except (EmptyFileError, OSError):
        await safe_send_message(config.ARINA_ID, templates.DREAMS_FILE_ERROR)
        raise
    except ValueError:
        await safe_send_message(
            config.ARINA_ID,
            templates.DELETE_DREAMS_REQUEST_IS_INVALID,
        )
        raise
    await state.clear()
    for message in deleted_dreams:
        if await safe_send_message(config.ARINA_ID, message) is None:
            break
    else:
        await safe_send_message(
            config.ARINA_ID,
            templates.CONTENT_IS_DELETED,
            keyboard=Arina_keyboard,
        )
