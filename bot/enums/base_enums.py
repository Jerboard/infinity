from enum import Enum


# ключи к сообщениям
class Key(str, Enum):
    START = 'start'
    SELL = 'sell'
    SELECT_CURRENCY = 'select_currency'
    SEND_SUM_BTC = 'send_sum_btc'
    SEND_SUM_LTC = 'send_sum_ltc'
    SEND_SUM_XMR = 'send_sum_xmr'
    SEND_SUM_USDT = 'send_sum_usdt'
    SELECT_PAY_METHOD = 'select_pay_method'
    EXCHANGE = 'exchange'
    SEND_WALLET = 'send_wallet'
    PAYMENT = 'payment'
    PAYMENT_CONF = 'payment_conf'
    FAIL_ORDER = 'fail_order'
    SUC_ORDER = 'suc_order'
    ACCOUNT = 'account'
    PROMO = 'promo'
    REPLACE_PROMO_CONF = 'replace_promo_conf'
    REPLACE_PROMO = 'replace_promo'
    PARTNER = 'partner'
    CASHBACK = 'cashback'
    TAKE_BONUS = 'take_bonus'
    TAKE_BONUS_CONF = 'take_bonus_conf'
    TAKE_BONUS_END = 'take_bonus_end'
    HISTORY = 'history'
    ANTISPAM = 'antispam'
    INFO = 'info'

    SUM_EXCHANGE = 'sum_exchange'

    # SAVE_PAY_METHOD = 'save_pay_method'

    CHECK_WALLET = 'check_wallet'
    ADD_PROMO = 'add_promo'


# действия
class InputType(str, Enum):
    RUB = 'rub'
    COIN = 'coin'


# действия
class Action(str, Enum):
    ADD = 'add'
    DEL = 'del'
    BACK = 'back'
    SEND = 'send'


# монеты
class Coin(str, Enum):
    BTC = 'BTC'
    ETH = 'ETH'
    LTC = 'LTC'
    XMR = 'XMR'
    USDT = 'USDT'


# статусы заказов
class OrderStatus(str, Enum):
    NOT_CONF = 'not_conf'
    NEW = 'new'
    PROC = 'processing'
    CANCEL = 'cancel'
    SUC = 'successful'
    FAIL = 'failed'


order_status_dict = {
    OrderStatus.NOT_CONF.value: 'Ожидает оплаты',
    OrderStatus.NEW.value: 'Оплачен',
    OrderStatus.SUC.value: 'Завершён',
    OrderStatus.FAIL.value: 'Отменён'
}


# статусы заказов
class MainButton(str, Enum):
    EXCHANGE = 'КУПИТЬ'
    SELL = 'ПРОДАТЬ'
    ACCOUNT = 'ЛИЧНЫЙ КАБИНЕТ'
    ANTISPAM = 'АНТИСПАМ БОТ'
    INFO = 'КОНТАКТЫ'


# Типы методов оплаты
class RequestMethodType(Enum):
    CARD = "card"
    SBP = "sbp"
    INT = "int"


request_method_dict = {
    RequestMethodType.CARD.value: 'По номеру карты',
    RequestMethodType.SBP.value: 'СБП',
    RequestMethodType.INT.value: 'Международная карта',
}


class PaymentStatus(Enum):
    PROC = "processing"
    SUCCESS = "success"
    NO_FUNDS = "no_funds"
    CANCELED = "canceled"
    WAITING = "waiting"
    ERROR = "error"
