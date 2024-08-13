from enum import Enum


# ключи к сообщениям
class CB(str, Enum):
    EXCHANGE = 'exchange'
    SETTINGS = 'settings'
    ANTISPAM = 'antispam'
    CONTACTS = 'contacts'


