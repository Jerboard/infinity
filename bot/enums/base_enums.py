from enum import Enum


# ключи к сообщениям
class Key(str, Enum):
    START = 'start'
    SELECT_CURRENCY = 'select_currency'
    SEND_SUM = 'send_sum'
    SUM_EXCHANGE = 'sum_exchange'
    SAVE_PAY_METHOD = 'save_pay_method'
    CHECK_WALLET = 'check_wallet'
    ADD_PROMO = 'add_promo'
    PAYMENT = 'payment'
    PAYMENT_CONF = 'payment_conf'
    SUC_ORDER = 'suc_order'
    FAIL_ORDER = 'fail_order'


# действия
class Action(str, Enum):
    ADD = 'add'
    DEL = 'del'
    BACK = 'back'


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

