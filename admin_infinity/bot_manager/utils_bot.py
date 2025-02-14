from enums import OrderStatus
from .models import Order, CashbackOrder


def proc_order(data: dict):
    if data.get('action') == 'del':
        edit_order = Order.objects.get(id=data['id'])
        if edit_order.status in [OrderStatus.NOT_CONF.value, OrderStatus.NEW.value]:
            edit_order.status = 'cancel'
            edit_order.save()

    elif data.get('action') == 'ok':
        edit_order = Order.objects.get(id=data['id'])
        if edit_order.status in [OrderStatus.NOT_CONF.value, OrderStatus.NEW.value]:
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
