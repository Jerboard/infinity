from aiogram import Dispatcher

import asyncio
import sys
import logging

from handlers import dp
from config import Config
from init import set_main_menu, bot, log_error
from db.base import init_models
from db.temp import update_db
from utils.scheduler_utils import scheduler_start_async, hand_orders
from utils.base_utils import amount_calculator


async def main() -> None:
    # amount_calculator(
    #     coin_rate=6000,
    #     user_rub_sum=5000,
    #     commission=10,
    #     infinity_percent=10,
    #     coin_round=8,
    #     buy_rate=6300,
    #     cashback_rate=0.01,
    #     promo_rate=80,
    #     use_balance=500
    # )
    # await update_db()
    # await hand_orders()
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
