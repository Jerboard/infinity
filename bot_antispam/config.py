import os
import pytz


DEBUG = bool(int(os.getenv('DEBUG')))


class Config:
    if DEBUG:
        token = os.getenv ("TOKEN_ANTISPAM")
        antispam_chat: int = int(os.getenv("MANAGER_ID_TEST"))
    else:
        token = os.getenv("TOKEN_ANTISPAM")
        antispam_chat: int = int(os.getenv("MANAGER_ID"))

    debug = DEBUG
    tz = pytz.timezone('Europe/Moscow')
    bot_id = int(token.split(":")[0])
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('POSTGRES_DB')
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_url = f'postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    datetime_form = '%d.%m.%Y %H:%M:%S'

