import asyncio
import sys
import logging

from handlers import dp
from config import Config
from init import bot, log_error


async def main() -> None:
    if not Config.debug:
        await bot.delete_webhook (drop_pending_updates=True)
        await dp.start_polling(bot)


if __name__ == "__main__":
    if Config.debug:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    else:
        log_error('start_bot', with_traceback=False)
    asyncio.run(main())
