from datetime import datetime, timedelta

import os

import db
from init import bot, log_error
import keyboards as kb
from config import Config
from .msg_utils import send_msg
from .google_utils import add_order_row, add_cd_order_row
from enums import OrderStatus, Key


def get_profit_exchange(coin_sum: float, buy_price: float, total_amount: float, commission: float) -> int:
    # прибыль
    buy_price = coin_sum * buy_price
    return round((total_amount - commission) - buy_price)


# Завершает заявку
async def done_order(order: db.OrderRow):
    user = await db.get_user_info(order.user_id)

    await db.update_order(order_id=order.id, status=OrderStatus.SUC.value)

    msg_data = await db.get_msg(Key.SUC_ORDER.value)
    text = msg_data.text.format(order_id=order.id, order_hash=order.hash)

    await send_msg(
        msg_data=msg_data,
        chat_id=order.user_id,
        text=text,
        keyboard=kb.get_done_order_kb()
    )

    # начисляем кешбек
    if order.cashback > 0:
        await db.update_user_info(user_id=order.user_id, add_cashback=order.cashback)
        await db.update_order(order_id=order.id, add_cashback=order.cashback)

    # реферальные баллы
    if user.referrer and order.profit > 0:
        referrer = await db.get_user_info(user_id=user.referrer)

        if referrer.custom_referral_lvl_id:
            lvl = await db.get_referral_lvl(lvl_id=referrer.custom_referral_lvl_id)

        else:
            referrals = await db.get_users(referrer=user.referrer)
            lvl = await db.get_referral_lvl(count_user=len(referrals))

        if lvl:
            ref_points = round(order.profit * (lvl.percent / 100))

            await db.update_user_info(user_id=referrer.user_id, add_point=ref_points)
            await db.update_order(order_id=order.id, add_ref_points=ref_points)

#     обновить статус в гугл
    order = await db.get_order(order.id)
    add_order_row(order=order, row=order.row)


# Отменяет заявку
async def del_order(order: db.OrderRow):
    used_points = order.used_points or 0
    used_cashback = order.used_cashback or 0

    if used_points > 0 or used_cashback > 0:
        await db.update_user_info(user_id=order.user_id, add_point=order.used_points, add_cashback=order.used_cashback)

    if order.promo:
        await db.update_used_promo(promo_id=order.promo_used_id, used=False)

    await db.update_order(order_id=order.id, status=OrderStatus.FAIL.value)

    msg_data = await db.get_msg(Key.FAIL_ORDER.value)
    text = msg_data.text.format(order_id=order.id)

    try:
        await bot.delete_message(chat_id=order.user_id, message_id=order.message_id)
    except Exception as ex:
        log_error(ex)

    await send_msg(
        msg_data=msg_data,
        chat_id=order.user_id,
        text=text
    )
    #     обновить статус в гугле
    order = await db.get_order(order.id)
    add_order_row(order=order, row=order.row)


# Удаляет просроченые заявки
async def del_old_orders():
    orders = await db.get_orders(old_orders=True)
    for order in orders:
        await del_order(order)


# сообщает об обработке сообщений
async def hand_orders():
    orders = await db.get_orders(for_done=True)
    for order in orders:
        if order.status == OrderStatus.PROC:
            await done_order(order)

        elif order.status == OrderStatus.CANCEL:
            await del_order(order)


# сообщает об обработке кешбека
async def hand_cashback_orders():
    orders = await db.get_cb_orders(for_done=True)
    for order in orders:
        try:
            if order.status == OrderStatus.PROC:
                await db.update_cb_orders(order_id=order.id, status=OrderStatus.SUC.value)

                msg_data = await db.get_msg(Key.SUC_ORDER.value)
                text = 'Бонусы отправлены'
                await send_msg(
                    msg_data=msg_data,
                    chat_id=order.user_id,
                    text=text
                )

            elif order.status == OrderStatus.CANCEL:
                await db.update_cb_orders(order_id=order.id, status=OrderStatus.FAIL.value)
                # await db.update_user_info(user_id=order.user_id, add_balance=order.sum)

                await db.update_user_info(
                    user_id=order.user_id,
                    add_point=order.points,
                    add_cashback=order.cashback
                )


                text = f'Ваш заказ № {order.id} ОТМЕНЕН.\n'

                await send_msg(
                    msg_key=Key.FAIL_ORDER.value,
                    chat_id=order.user_id,
                    text=text
                )

            # добавляем в таблицу
            order_cb = await db.get_cb_order(order.id)
            add_cd_order_row(order_cb, row=order_cb.row)

        except Exception as ex:
            log_error(f'Не удалось обработать заявку\n{ex}', with_traceback=False)


# палит документ и отправляет его
async def send_doc():
    # admin = '1879617805'
    # admins = [524275902,]
    admins = [2028268703, 1879617805]

    path = 'temp'
    dir = os.listdir(path)
    if len(dir) > 0:
        for file in dir:
            file_path = os.path.join(path, file)
            for admin in admins:
                try:
                    with open(file_path, 'rb') as open_file:
                        await bot.send_document(chat_id=admin, document=open_file)
                except Exception as ex:
                    log_error(f'async_utils 180: {ex} for user {admin}', with_traceback=False)

            os.remove(file_path)  # Удаляем файл после отправки
