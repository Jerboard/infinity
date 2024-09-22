from pytz import timezone

import os


DEBUG = bool(int(os.getenv('DEBUG')))


class Config:
    if DEBUG:
        # token = os.getenv ("TOKEN_TEST")
        token = '7377609086:AAGDLKGKNTeruBfGNYOr4O-FO1kt7-9gtYI'
        access_chat = -1001669708234
        bot_link = 'https://t.me/tushchkan_test_4_bot'
        bot_id = 7377609086
        antispam_chat = 5772948261
    else:
        token = os.getenv ("TOKEN")
        access_chat = int(os.getenv('ACCESS_CHAT'))
        bot_link = 'https://t.me/tushchkan_test_4_bot'
        bot_id = 7377609086
        antispam_chat = 575386391

    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('POSTGRES_DB')
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_url = f'postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    tz = timezone('Asia/Tashkent')
    api_key_cm = os.getenv('API_KEY_COINMARKET')
    operator_url = os.getenv('OPERATOR')
    batch_size = 3

    test_photo = 'AgACAgIAAxkBAAMKZtwCcBYQoPHYC7QXVMDvHPk4TO0AAtHdMRtgheBKwXbCeNk2bWEBAAMCAAN4AAM2BA'  # @tushchkan_test_4_bot

    @property
    def debug(self) -> bool:
        return DEBUG

    # day_form = '%d.%m'
    # date_form = '%d.%m.%Y'
    # datetime_form = '%d.%m.%Y %H:%M'
    # time_form = '%H:%M'
