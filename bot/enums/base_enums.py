from enum import Enum


# ключи к сообщениям
class Key(str, Enum):
    START = 'start'
    SELL = 'sell'
    SELECT_CURRENCY = 'select_currency'
    SEND_SUM = 'send_sum'
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

