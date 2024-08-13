from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from enums import CB


# Стартовая клавиатура
def get_start_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='ОБМЕН', callback_data=CB.EXCHANGE.value)
    kb.button(text='ЛИЧНЫЙ КАБИНЕТ', callback_data=CB.SETTINGS.value)
    kb.button(text='АНТИСПАМ БОТ', callback_data=CB.ANTISPAM.value)
    kb.button(text='КОНТАКТЫ', callback_data=CB.CONTACTS.value)
    return kb.adjust(1, 1, 2).as_markup()
