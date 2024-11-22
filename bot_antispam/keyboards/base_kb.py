from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

# import db
# from config import Config
from enums import CB, Action


# Антиспам кнопки админ
def get_antispam_admin_kb(user_id: int, on: bool = True) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if on:
        kb.button(text=f'📲 Ответить', callback_data=f'{CB.ADMIN_ANTISPAM.value}:{Action.SEND.value}:{user_id}')
    else:
        kb.button(text=f'❌ Отмена', callback_data=f'{CB.ADMIN_ANTISPAM.value}:{Action.DEL.value}:{user_id}')
    return kb.adjust(1).as_markup()