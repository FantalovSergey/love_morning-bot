from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

GET_CUTENESS_TEXT = 'Получить милоту райт нау!!'
SHOW_MESSAGES_TEXT = 'Посмотреть сообщения'
DELETE_MESSAGES_TEXT = 'Удалить сообщения'
CANCEL_TEXT = 'Отмена'

get_cuteness = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=GET_CUTENESS_TEXT)]],
    resize_keyboard=True,
)

show_messages = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=SHOW_MESSAGES_TEXT)]],
    resize_keyboard=True,
)

delete_messages = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=DELETE_MESSAGES_TEXT)]],
    resize_keyboard=True,
)

cancel = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=CANCEL_TEXT)]],
    resize_keyboard=True,
)
