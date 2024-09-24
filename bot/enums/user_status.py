from enum import Enum


# ключи к сообщениям
class UserStatus(str, Enum):
    EXCHANGE = 'exchange'
    EXCHANGE_SEND_SUM = 'exchange_send_sum'
    EXCHANGE_SEND_WALLET = 'exchange_send_wallet'
    EXCHANGE_SEND_PROMO = 'exchange_send_promo'
    ACC_PROMO = 'acc_promo'
    TAKE_CASHBACK = 'take_cashback'
    ANTISPAM = 'antispam'
    FEEDBACK = 'feedback'
