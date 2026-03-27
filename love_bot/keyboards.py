from aiogram.types import KeyboardButton as Button, ReplyKeyboardMarkup

GET_CUTENESS = 'Получить милоту райт нау!!'
WRITE_DREAM = 'Записать сон📝'
SHOW_MESSAGES = 'Посмотреть сообщения'
SHOW_DREAMS = 'Посмотреть все сны😴'
DELETE_MESSAGES = 'Удалить сообщения'
DELETE_DREAMES = 'Удалить нехорошие сны🗑️'
WRITE_AS_BOT = 'Написать от лица бота'
CANCEL = 'Отмена❌'

Arina_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [Button(text=GET_CUTENESS), Button(text=SHOW_DREAMS)],
        [Button(text=WRITE_DREAM), Button(text=DELETE_DREAMES)],
    ],
    resize_keyboard=True,
)

my_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [Button(text=SHOW_MESSAGES), Button(text=SHOW_DREAMS)],
        [Button(text=DELETE_MESSAGES), Button(text=WRITE_AS_BOT)],
    ],
    resize_keyboard=True,
)

cancel = ReplyKeyboardMarkup(
    keyboard=[[Button(text=CANCEL)]], resize_keyboard=True,
)
