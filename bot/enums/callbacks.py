from enum import Enum


# ключи к сообщениям
class CB(str, Enum):
    CAPCHA = 'capcha'
    BACK_START = 'back_start'
    EXCHANGE = 'exchange'
    SETTINGS = 'settings'
    ANTISPAM = 'antispam'
    CONTACTS = 'contacts'
    SELECT_PAYMENT = 'select_payment'
    SEND_WALLET = 'send_wallet'
    PAYMENT_ADD = 'payment_add'
    ADD_PROMO = 'add_promo'
    USE_CASHBACK = 'use_cashback'
    BACK_CHECK_INFO = 'back_check_info'
    PAYMENT_CONF = 'payment_conf'



