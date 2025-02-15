from pytz import timezone

import os


DEBUG = bool(int(os.getenv('DEBUG')))


class Config:
    if DEBUG:
        token = os.getenv ("TOKEN_TEST")
        access_chat = os.getenv ("ACCESS_CHAT_TEST")
        bot_link = 'https://t.me/tushchkan_test_4_bot'
        antispam_chat = os.getenv("MANAGER_ID_TEST")
        operator_chat = os.getenv("OPERATOR_ID_TEST")
        antispam_url = 'https://t.me/infinity_support24_bot'
        feedback_chat = int(os.getenv("FEEDBACK_CHAT_TEST"))
        feedback_check_chat = int(os.getenv("FEEDBACK_CHECK_CHAT_ID_TEST"))
        get_table_id = os.getenv ("TABLE_TEST")
        api_key_cm = os.getenv('API_KEY_COINMARKET_TEST')
        order_live_time = 20
        # api_url = 'http://127.0.0.1:8000/'
        api_url = 'http://62.217.181.79/'
    else:
        token = os.getenv("TOKEN")
        access_chat = os.getenv ("ACCESS_CHAT")
        bot_link = 'https://t.me/Infinity_exchange_bot'
        antispam_chat = os.getenv("MANAGER_ID")
        operator_chat = os.getenv("OPERATOR_ID")
        antispam_url = 'https://t.me/infinity_support24_bot'
        feedback_check_chat = int(os.getenv("FEEDBACK_CHECK_CHAT_ID"))
        feedback_chat = int(os.getenv("FEEDBACK_CHAT"))
        get_table_id = os.getenv("TABLE")
        api_key_cm = os.getenv('API_KEY_COINMARKET')
        order_live_time = 30
        api_url = 'http://62.217.181.79/'

    debug = DEBUG

    bot_id = int(token.split(":")[0])
    tz = timezone('Europe/Moscow')
    batch_size = 3

    file_google_path = os.path.join('data', 'sheet_key.json')

    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('POSTGRES_DB')
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_url = f'postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')

    endpoint_details = "api/v1/payment-details/"
    endpoint_close = "api/v1/payment-close/"

    operator_url = os.getenv('OPERATOR')
    channel = os.getenv('CHANNEL')

    datetime_form = '%d.%m.%Y %H:%M:%S'

    test_photo = 'AgACAgIAAxkBAAMKZtwCcBYQoPHYC7QXVMDvHPk4TO0AAtHdMRtgheBKwXbCeNk2bWEBAAMCAAN4AAM2BA'  # @tushchkan_test_4_bot
