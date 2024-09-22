import os, csv
from datetime import datetime


def export(orders):
    names_columns = ['ID', 'Время', 'Статус', 'ID Пользователя', 'Пользователь', 'Валюта', 'Способ оплаты', 'Сумма валюты',
                     'Кошелёк', 'Промокод', 'Курс', 'Процент наценки', 'Сумма', 'Промо скидка', 'Списано баллов', 'Итог',
                     'Хеш', 'Комиссия', 'Кешбэк', 'Прибыль']

    file_path = f'/home/bot/temp/orders-{datetime.now().date()}.csv'

    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(names_columns)

        for order in orders:
            row = [order.id, order.time, order.status, order.user_id, order.name_user, order.coin,
                   order.pay_method, order.coin_sum, order.wallet, order.promo, order.exchange_rate,
                   order.percent, order.amount, order.promo_rate, order.used_points, order.total_amount,
                   order.hash, order.commission, order.cashback, order.profit]
            writer.writerow(row)


