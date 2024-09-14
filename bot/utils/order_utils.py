from datetime import datetime, timedelta

import os

import db
from init import bot, log_error
from .msg_utils import send_msg
from enums import OrderStatus, Key


# Отменяет заявку
async def del_order(order: db.OrderRow):
    if order.used_points > 0 or order.used_cashback > 0:
        await db.update_user_info(user_id=order.user_id, add_point=order.used_points, add_cashback=order.used_cashback)

    if order.promo:
        await db.update_used_promo(promo_id=order.promo_used_id, used=False)

    await db.update_orders(order_id=order.id, status=OrderStatus.FAIL.value)

    msg_data = await db.get_msg(Key.FAIL_ORDER.value)
    text = msg_data.text.format(order_id=order.id)

    try:
        await bot.delete_message(chat_id=order.user_id, message_id=order.message_id)
    except Exception as ex:
        pass

    await send_msg(
        msg_data=msg_data,
        chat_id=order.user_id,
        text=text
    )


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
            await db.update_orders(order_id=order.id, status=OrderStatus.SUC.value)

            msg_data = await db.get_msg(Key.SUC_ORDER.value)
            text = msg_data.text.format(
                order_id=order.id,
                order_hash=order.hash
            )

            # await bot.delete_message(chat_id=order.user_id, message_id=order.message_id)
            await send_msg(
                msg_data=msg_data,
                chat_id=order.user_id,
                text=text
            )

        else:
            await del_order(order)


# сообщает об обработке кешбека
async def hand_cashback_orders():
    orders = await db.get_cb_orders(for_done=True)
    for order in orders:
        try:
            if order.status == OrderStatus.PROC:
                await db.update_cb_orders(order_id=order.id, status=OrderStatus.SUC.value)

                text = f'Ваша заявка № {order.id} выполнена\n\n'

                try:
                    await bot.delete_message(chat_id=order.id, message_id=order.id)
                except Exception as ex:
                    pass

                await send_msg(
                    msg_key=Key.SUC_ORDER.value,
                    chat_id=order.user_id,
                    text=text
                )

            elif order.status == OrderStatus.CANCEL:
                await db.update_cb_orders(order_id=order.id, status=OrderStatus.FAIL.value)
                await db.update_user_info(user_id=order.user_id, add_balance=order.sum)

                text = f'Ваш заказ № {order.id} ОТМЕНЕН.\n'

                try:
                    await bot.delete_message(chat_id=order.user_id, message_id=order.message_id)
                except Exception as ex:
                    pass

                await send_msg(
                    msg_key=Key.FAIL_ORDER.value,
                    chat_id=order.user_id,
                    text=text
                )

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