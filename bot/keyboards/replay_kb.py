from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from enums import MainButton


# Стартовая клавиатура
def get_start_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True, keyboard=[
        [KeyboardButton(text=MainButton.EXCHANGE.value), KeyboardButton(text=MainButton.SELL.value)],
        [KeyboardButton(text=MainButton.ACCOUNT.value)],
        [KeyboardButton(text=MainButton.ANTISPAM.value), KeyboardButton(text=MainButton.INFO.value)],
    ])
