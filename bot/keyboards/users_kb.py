from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

import db
from enums import CB, Action


# Клавиатура с капчой
def get_capcha_kb(items: list[list], match: dict, referrer) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for item in items:
        if item == match:
            kb.button(text=item[1], callback_data=f'{CB.CONTACTS.value}:{referrer}')
        else:
            kb.button(text=item[1], callback_data=f'{CB.CONTACTS.value}:0')

    return kb.adjust(3).as_markup()


# Стартовая клавиатура
def get_start_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='ОБМЕН', callback_data=CB.EXCHANGE.value)
    kb.button(text='ЛИЧНЫЙ КАБИНЕТ', callback_data=CB.SETTINGS.value)
    kb.button(text='АНТИСПАМ БОТ', callback_data=CB.ANTISPAM.value)
    kb.button(text='КОНТАКТЫ', callback_data=CB.CONTACTS.value)
    return kb.adjust(1, 1, 2).as_markup()


# назад
def get_back_kb(cb: str, arg: str = Action.BACK.value):
    kb = InlineKeyboardBuilder()
    kb.button(text=f'🔙 Назад', callback_data=f'{cb}:{arg}')
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
def get_pay_method_kb(sum_rub: float, pay_methods: tuple[db.PayMethodRow]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for pay_method in pay_methods:
        kb.button(text=f'{pay_method.name} ({sum_rub} руб.)', callback_data=f'{CB.SEND_WALLET.value}:{pay_method.id}')

    kb.button(text='🔙 Назад', callback_data=f'{CB.SELECT_PAYMENT.value}:{Action.BACK.value}')
    return kb.adjust(1).as_markup()


# клавиатура проверки данный
def get_check_info_kb(use_points: bool, points: int, promo: str = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Все верно', callback_data=CB.PAYMENT_ADD.value)
    if not promo:
        kb.button(text='Есть промокод', callback_data=CB.ADD_PROMO.value)
    if points and not use_points:
        kb.button(text=f'Использовать баллы ({points})', callback_data=CB.USE_CASHBACK.value)
    kb.button(text='🔙 Назад', callback_data=f'{CB.SEND_WALLET.value}:{Action.BACK.value}')

    return kb.adjust(1).as_markup()


# подтвердить оплату
def get_payment_conf_kb(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f'✅ Я оплатил', callback_data=f'{CB.PAYMENT_CONF.value}:{order_id}:{Action.ADD.value}')
    kb.button(text=f'❌ Удалить заявку', callback_data=f'{CB.PAYMENT_CONF.value}:{order_id}:{Action.DEL.value}')
    kb.button(text=f'🔙 Назад', callback_data=f'{CB.BACK_CHECK_INFO.value}')

    return kb.adjust(1).as_markup()


# админская кб отправки сообщений
def get_sending_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='📲Отправить всем пользователям', callback_data=f'{CB.SENDING_MESSAGE.value}:{Action.SEND.value}')
    kb.button(text='🗑Удалить сообщение', callback_data=f'{CB.SENDING_MESSAGE.value}:{Action.DEL.value}')
    return kb.adjust(1).as_markup()