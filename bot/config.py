from pytz import timezone

import os


DEBUG = bool(int(os.getenv('DEBUG')))


class Config:
    if DEBUG:
        token = os.getenv ("TOKEN_TEST")
        access_chat = -1001669708234
    else:
        token = os.getenv ("TOKEN")
        access_chat = int(os.getenv('ACCESS_CHAT'))

    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('POSTGRES_DB')
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_url = f'postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    tz = timezone('Asia/Tashkent')
    api_key_cm = os.getenv('API_KEY_COINMARKET')

    @property
    def debug(self) -> bool:
        return DEBUG


    # day_form = '%d.%m'
    # date_form = '%d.%m.%Y'
    # datetime_form = '%d.%m.%Y %H:%M'
    # time_form = '%H:%M'
