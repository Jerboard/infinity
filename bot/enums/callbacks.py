from enum import Enum


# ключи к сообщениям
class CB(str, Enum):
    CAPCHA = 'capcha'
    BACK_START = 'back_start'
    EXCHANGE = 'exchange'
    SETTINGS = 'settings'
    ANTISPAM = 'antispam'
    CONTACTS = 'contacts'


