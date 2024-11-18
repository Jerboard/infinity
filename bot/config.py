from pytz import timezone

import os


DEBUG = bool(int(os.getenv('DEBUG')))


class Config:
    if DEBUG:
        token = os.getenv ("TOKEN_TEST")
        access_chat = os.getenv ("ACCESS_CHAT_TEST")
        bot_link = 'https://t.me/tushchkan_test_4_bot'
        antispam_chat = os.getenv("MANAGER_ID_TEST")
        feedback_chat = int(os.getenv("FEEDBACK_CHAT_TEST"))
        get_table_id = os.getenv ("TABLE_TEST")
    else:
        token = os.getenv("TOKEN_TEST")
        access_chat = os.getenv ("ACCESS_CHAT_TEST")
        bot_link = 'https://t.me/tushchkan_test_4_bot'
        antispam_chat = os.getenv("MANAGER_ID")
        feedback_chat = int(os.getenv("FEEDBACK_CHAT_TEST"))
        get_table_id = os.getenv("TABLE_TEST")

    debug = DEBUG
    bot_id = int(token.split(":")[0])
    file_google_path = os.path.join('data', 'sheet_key.json')
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
    channel = os.getenv('CHANNEL')
    datetime_form = '%d.%m.%Y %H:%M:%S'

    test_photo = 'AgACAgIAAxkBAAMKZtwCcBYQoPHYC7QXVMDvHPk4TO0AAtHdMRtgheBKwXbCeNk2bWEBAAMCAAN4AAM2BA'  # @tushchkan_test_4_bot
