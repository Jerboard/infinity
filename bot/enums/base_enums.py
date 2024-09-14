from enum import Enum


# ключи к сообщениям
class Key(str, Enum):
    START = 'start'
    SELL = 'sell'
    SELECT_CURRENCY = 'select_currency'
    SEND_SUM = 'send_sum'
    SUM_EXCHANGE = 'sum_exchange'
    EXCHANGE = 'exchange'
    # SAVE_PAY_METHOD = 'save_pay_method'
    SEND_WALLET = 'send_wallet'
    CHECK_WALLET = 'check_wallet'
    ADD_PROMO = 'add_promo'
    REPLACE_PROMO = 'replace_promo'
    PAYMENT = 'payment'
    PAYMENT_CONF = 'payment_conf'
    SUC_ORDER = 'suc_order'
    FAIL_ORDER = 'fail_order'
    ACCOUNT = 'account'
    PROMO = 'promo'
    PARTNER = 'partner'
    CASHBACK = 'cashback'
    TAKE_BONUS = 'take_bonus'
    TAKE_BONUS_CONF = 'take_bonus_conf'
    TAKE_BONUS_END = 'take_bonus_end'
    HISTORY = 'history'


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

