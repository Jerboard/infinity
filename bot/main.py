from aiogram import Dispatcher

import asyncio
import sys
import logging

from handlers import dp
from config import Config
from init import set_main_menu, bot, log_error
from db.base import init_models
from db.temp import update_db
from utils.scheduler_utils import scheduler_start_async


async def main() -> None:
    # await update_db()
    await init_models()
    await set_main_menu()
    if not Config.debug:
        await scheduler_start_async()
    # await scheduler_start_async()

    await bot.delete_webhook (drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    if Config.debug:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    else:
        log_error('start_bot', with_traceback=False)
    asyncio.run(main())
