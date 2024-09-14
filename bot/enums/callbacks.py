from enum import Enum


# ключи к сообщениям
class CB(str, Enum):
    CAPCHA = 'capcha'
    BACK_START = 'back_start'
    EXCHANGE = 'exchange'
    SELL = 'sell'
    ACCOUNT = 'account'
    ANTISPAM = 'antispam'
    CONTACTS = 'contacts'
    SELECT_PAYMENT = 'select_payment'
    SEND_WALLET = 'send_wallet'
    PAYMENT_ADD = 'payment_add'
    USE_PROMO = 'use_promo'
    USE_CASHBACK = 'use_cashback'
    BACK_CHECK_INFO = 'back_check_info'
    PAYMENT_CONF = 'payment_conf'
    SENDING_MESSAGE = 'sending_message'
    PROMO = 'promo'
    PARTNER = 'partner'
    CASHBACK = 'cashback'
    TAKE_BONUS = 'take_bonus'
    TAKE_BONUS_CONF = 'conf_take_bonus'
    HISTORY = 'history'
    GAMBLING = 'gambling'
    REPLACE_PROMO = 'replace_promo'



