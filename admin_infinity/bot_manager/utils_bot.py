from datetime import datetime

import os

from admin_infinity.settings import redis_client, CHANNEL
from .export_file import export
from .models import Order, Currency, PayMethod, Promo, User, CashbackLevel, CashbackOrder


def proc_order(data: dict):
    if data.get('action') == 'del':
        edit_order = Order.objects.get(id=data['id'])
        edit_order.status = 'cancel'
        edit_order.save()

    elif data.get('action') == 'ok':
        edit_order = Order.objects.get(id=data['id'])
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
