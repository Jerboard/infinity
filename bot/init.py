from aiogram import Dispatcher
from aiogram.types.bot_command import BotCommand
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, Redis

from apscheduler.schedulers.asyncio import AsyncIOScheduler
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

redis_aiogram = Redis(host=Config.redis_host, port=Config.redis_port, db=0)
storage = RedisStorage(redis=redis_aiogram)

loop = asyncio.get_event_loop()
# dp = Dispatcher(storage=storage, loop=loop)
dp = Dispatcher(loop=loop)
bot = Bot(Config.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

scheduler = AsyncIOScheduler(timezone=Config.tz)
ENGINE = create_async_engine(url=Config.db_url)

# redis_client = aioredis.Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')), db=0)


async def set_main_menu():
    main_menu_commands = [
        BotCommand(command='/start', description='В начало'),
    ]

    await bot.set_my_commands(main_menu_commands)


# запись ошибок
def log_error(message, with_traceback: bool = True):
    now = datetime.now(Config.tz)
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
