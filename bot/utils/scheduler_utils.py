from init import scheduler

from .coin_utils import update_currency_rate
from .order_utils import del_old_orders, hand_orders, hand_cashback_orders


# Запуск шедулеров
async def scheduler_start_async():
    # scheduler_async.add_job(check_sub, "cron", hour=22)
    scheduler.add_job(update_currency_rate, "interval", minutes=5)
    scheduler.add_job(del_old_orders, "interval", minutes=1)
    scheduler.add_job(hand_orders, "interval", seconds=20)
    scheduler.add_job(hand_cashback_orders, "interval", seconds=20)
    # scheduler.add_job(send_doc, "interval", seconds=20)
    scheduler.start()
