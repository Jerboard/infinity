from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

import db
from config import Config
from enums import CB, Action


# Клавиатура с капчой
def get_capcha_kb(items: list[list], match: dict, referrer) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for item in items:
        if item == match:
            kb.button(text=item[1], callback_data=f'{CB.CAPCHA.value}:1:{referrer}')
        else:
            kb.button(text=item[1], callback_data=f'{CB.CAPCHA.value}:0:{referrer}')

    return kb.adjust(3).as_markup()


# Стартовая клавиатура
def get_start_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='КУПИТЬ', callback_data=CB.EXCHANGE.value)
    kb.button(text='ПРОДАТЬ', callback_data=CB.SELL.value)
    kb.button(text='ЛИЧНЫЙ КАБИНЕТ', callback_data=CB.ACCOUNT.value)
    kb.button(text='АНТИСПАМ БОТ', callback_data=CB.ANTISPAM.value)
    kb.button(text='КОНТАКТЫ', callback_data=CB.CONTACTS.value)
    return kb.adjust(2, 1, 2).as_markup()


# клавиатура ЛК
def get_account_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='ПРОМОКОД', callback_data=CB.PROMO.value)
    kb.button(text='ПАРТНЁРСКАЯ ПРОГРАММА', callback_data=CB.PARTNER.value)
    kb.button(text='КЕШБЭК', callback_data=CB.CASHBACK.value)
    kb.button(text='ВЫВОД БОНУСОВ', callback_data=CB.TAKE_BONUS.value)
    kb.button(text='ИСТОРИЯ ОБМЕНОВ', callback_data=f'{CB.HISTORY.value}:0')
    kb.button(text='ИСПЫТАЙ УДАЧУ', callback_data=CB.GAMBLING.value)
    kb.button(text=f'🔙 НАЗАД', callback_data=f'{CB.BACK_START.value}')
    return kb.adjust(1).as_markup()


# назад
def get_back_kb(cb: str, arg: str = Action.BACK.value) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f'🔙 Назад', callback_data=f'{cb}:{arg}')
    return kb.adjust(1).as_markup()


# отмена
def get_cancel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f'❌ Отмена', callback_data=CB.CANCEL.value)
    return kb.adjust(1).as_markup()


# продать валюту
def get_sell_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f'Оператор', url=Config.operator_url)
    kb.button(text=f'🔙 Назад', callback_data=f'{CB.BACK_START.value}')
    return kb.adjust(1).as_markup()


# клавиатура со списком валют
def get_currency_list_kb(currencies: tuple[db.CurrencyRow]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for currency in currencies:
        kb.button(text=f'{currency.name} ({currency.code})', callback_data=f'{CB.SELECT_PAYMENT.value}:{currency.id}')

    back_bt = InlineKeyboardBuilder()
    back_bt.button(text='🔙 Назад', callback_data=CB.BACK_START.value)
    return kb.adjust(2).attach(back_bt).as_markup()


# клавиатура со способами оплаты
# def get_pay_method_kb(sum_rub: float, pay_methods: tuple[db.PayMethodRow]) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     for pay_method in pay_methods:
#         kb.button(text=f'{pay_method.name} ({sum_rub} руб.)', callback_data=f'{CB.SEND_WALLET.value}:{pay_method.id}')
#
#     kb.button(text='🔙 Назад', callback_data=f'{CB.SELECT_PAYMENT.value}:{Action.BACK.value}')
#     return kb.adjust(1).as_markup()


# клавиатура проверки данный
# def get_check_info_kb(use_points: bool, points: int, promo: str = None) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text='✅ Все верно', callback_data=CB.PAYMENT_ADD.value)
#     if not promo:
#         kb.button(text='Есть промокод', callback_data=CB.USE_PROMO.value)
#     if points and not use_points:
#         kb.button(text=f'Использовать баллы ({points})', callback_data=CB.USE_CASHBACK.value)
#     kb.button(text='🔙 Назад', callback_data=f'{CB.SEND_WALLET.value}:{Action.BACK.value}')
#
#     return kb.adjust(1).as_markup()


# клавиатура проверки данный
def get_main_exchange_kb(total_amount: int, promo_id: str = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f'ПЕРЕЙТИ К ОПЛАТЕ ({total_amount} РУБ)', callback_data=CB.SEND_WALLET.value)
    if promo_id:
        kb.button(text='ИСП, ПРОМОКОД', callback_data=CB.USE_PROMO.value)

    kb.button(text=f'ИСП, БАЛАНС КОШЕЛЬКА', callback_data=CB.USE_CASHBACK.value)
    return kb.adjust(1).as_markup()


# подтвердить оплату
def get_payment_conf_kb(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f'Я ОПЛАТИЛ', callback_data=f'{CB.PAYMENT_CONF.value}:{order_id}:{Action.ADD.value}')
    kb.button(text=f'ОТМЕНИТЬ ЗАЯВКУ', callback_data=f'{CB.PAYMENT_CONF.value}:{order_id}:{Action.DEL.value}')

    return kb.adjust(1).as_markup()


# админская кб отправки сообщений
def get_sending_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='📲 Отправить всем пользователям', callback_data=f'{CB.SENDING_MESSAGE.value}:{Action.SEND.value}')
    kb.button(text='🗑 Удалить сообщение', callback_data=f'{CB.SENDING_MESSAGE.value}:{Action.DEL.value}')
    return kb.adjust(1).as_markup()


# Подтвердить замену промо
# def get_replace_promo_kb(old_promo_id: int, new_promo_id: int) -> InlineKeyboardMarkup:
def get_replace_promo_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f'Сменить промокод', callback_data=f'{CB.REPLACE_PROMO.value}')
    kb.button(text=f'🔙 Назад', callback_data=f'{CB.PROMO.value}')
    return kb.adjust(1).as_markup()


# Подтвердить замену промо
def get_conf_take_bonus_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f'Всё верно', callback_data=f'{CB.TAKE_BONUS_CONF.value}')
    kb.button(text=f'🔙 Назад', callback_data=f'{CB.TAKE_BONUS.value}')
    return kb.adjust(1).as_markup()


# Подтвердить замену промо
def get_history_kb(start: int, end_page: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    btn_count = 0
    if start > 0:
        btn_count += 1
        kb.button(text=f'ПРЕД СТР.', callback_data=f'{CB.HISTORY.value}:{start - Config.batch_size}')
    if not end_page:
        btn_count += 1
        kb.button(text=f'СЛЕД СТР.', callback_data=f'{CB.ACCOUNT.value}:{start + Config.batch_size}')

    kb.button(text=f'🔙 Назад', callback_data=f'{CB.ACCOUNT.value}')
    kb.adjust(2, 1) if btn_count == 2 else kb.adjust(1)
    return kb.as_markup()


# Антиспам кнопки пользователь
def get_antispam_user_kb(on: bool = True) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if on:
        kb.button(text=f'ЗАДАТЬ ВОПРОС', callback_data=f'{CB.ADMIN_ANTISPAM.value}:{Action.SEND.value}:{Config.antispam_chat}')
    else:
        kb.button(text=f'❌ Отмена', callback_data=f'{CB.ADMIN_ANTISPAM.value}:{Action.DEL.value}:{Config.antispam_chat}')

    kb.button(text=f'🔙 Назад', callback_data=f'{CB.BACK_START.value}')
    return kb.adjust(1).as_markup()


# Антиспам кнопки админ
def get_antispam_admin_kb(user_id: int, on: bool = True) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if on:
        kb.button(text=f'📲 Ответить', callback_data=f'{CB.ADMIN_ANTISPAM.value}:{Action.SEND.value}:{user_id}')
    else:
        kb.button(text=f'❌ Отмена', callback_data=f'{CB.ADMIN_ANTISPAM.value}:{Action.DEL.value}:{user_id}')
    return kb.adjust(1).as_markup()


