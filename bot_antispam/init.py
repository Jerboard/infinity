from aiogram import Dispatcher
from aiogram.types.bot_command import BotCommand
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from sqlalchemy.ext.asyncio import create_async_engine
from datetime import datetime

import logging
import traceback
import os
import asyncio
import re

from config import Config


try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    pass


loop = asyncio.get_event_loop()
dp = Dispatcher()
bot = Bot(Config.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

ENGINE = create_async_engine(url=Config.db_url)


# запись ошибок
def log_error(message, with_traceback: bool = True):
    now = datetime.now()
    log_folder = now.strftime ('%m-%Y')
    log_path = os.path.join('logs', log_folder)

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_file_path = os.path.join(log_path, f'{now.day}.log')
    logging.basicConfig (level=logging.WARNING, filename=log_file_path, encoding='utf-8')

    if with_traceback:
        ex_traceback = traceback.format_exc()
        tb = ''
        msg = ''
        start_row = '  File "/app'
        tb_split = ex_traceback.split('\n')
        for row in tb_split:
            if row.startswith(start_row) and not re.search ('venv', row):
                tb += f'{row}\n'

            if not row.startswith(' '):
                msg += f'{row}\n'

        logging.warning(f'>>error\n{now}\n{tb}\n\n{msg}\n---------------------------------\n')
        return msg
    else:
        logging.warning(f'{now}\n{message}\n\n---------------------------------\n')
