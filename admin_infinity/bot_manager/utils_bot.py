from datetime import datetime

import os
import logging

from admin_infinity.settings import redis_client, CHANNEL
from .export_file import export
from .models import Order, Currency, PayMethod, Promo, User, CashbackLevel, CashbackOrder


def proc_order(data: dict):
    redis_client.publish(CHANNEL, 'Hello, Redis!')

    if data.get('action') == 'del':
        edit_order = Order.objects.get(id=data['id'])
        edit_order.status = 'hand:del'
        edit_order.save()

    elif data.get('action') == 'ok':
        edit_order = Order.objects.get(id=data['id'])
        currency = Currency.objects.get(code=edit_order.coin)

        # считаем прибыль
        buy_price = edit_order.coin_sum * currency.buy_price
        profit = (edit_order.total_amount - edit_order.commission) - buy_price

        # кешбек
        user = User.objects.get(user_id=edit_order.user_id)

        if user.referrer is not None and profit > 0:

            referrer_id = user.referrer
            count_referals = len(User.objects.filter(referrer=referrer_id))

            referrer_info = User.objects.filter(user_id=referrer_id).first()

            if referrer_info.custom_refferal_lvl is not None:
                cashback_data = (CashbackLevel.objects.filter(id=referrer_info.custom_refferal_lvl.id).first())
            else:
                cashback_data = CashbackLevel.objects.filter(
                    count_users__lte=count_referals
                ).order_by('-count_users').first()

            # print(cashback_data)
            if cashback_data is None:
                max_cashback = CashbackLevel.objects.order_by('-count_users').first()
                if max_cashback.count_users <= count_referals:
                    cashback_data = max_cashback

            # print(cashback_data.percent)
            cashback = profit * (cashback_data.percent / 100)
            referrer = User.objects.get(user_id=referrer_id)

            referrer.balance = round(referrer.balance + cashback)
            referrer.save()

            logging.warning(f'User: {user.user_id}\n'
                            f'Username: {user.username}\n'
                            f'Cashback: {cashback}\n'
                            f'Cashback_data: {cashback_data.count_users} {cashback_data.percent}\n'
                            f'referrer_info: {referrer_info}')

        edit_order.profit = profit
        edit_order.hash = data['hash']
        edit_order.status = 'processing'
        edit_order.save()

    elif data.get('action') == 'ok_cb':
        order = CashbackOrder.objects.get(id=data.get('id'))
        order.status = 'processing'
        order.save()
    elif data.get('action') == 'del_cb':
        order = CashbackOrder.objects.get(id=data.get('id'))
        order.status = 'cancel'
        order.save()
