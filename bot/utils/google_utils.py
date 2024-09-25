from gspread.spreadsheet import Spreadsheet

import gspread

import db
from config import Config
from init import log_error


def get_google_connect() -> Spreadsheet:
    gc = gspread.service_account (filename=Config.file_google_path)
    return gc.open_by_key (Config.get_table_id)


def get_last_row_num(table: list[list[any]]) ->int:
    last_row = 3

    print(f'>>>>> {len(table)}')

    for row in table[2:]:
        last_row += 1
        if not str(row[0]).isdigit():
            break
    return last_row


# добавляет заказ в таблицу
def add_order_row(order: db.OrderRow) -> int:
    sh = get_google_connect()

    ggl_orders = sh.sheet1.get_all_values()
    last_row = get_last_row_num(ggl_orders)

    # изменяет статус заказа
    try:
        cell = f'A{last_row}:W{last_row}'
        new_row_str = [
            [
                str(order.id) if order.id else '', str(order.user_id) if order.user_id else '',
                str(order.status) if order.status else '', str(order.coin) if order.coin else '',
                str(order.pay_method) if order.pay_method else '', str(order.card) if order.card else '-',
                str(order.coin_sum) if order.coin_sum else '', str(order.wallet) if order.wallet else '',
                str(order.promo) if order.promo else '', str(order.promo_rate) if order.promo_rate else '',
                str(order.exchange_rate) if order.exchange_rate else '', str(order.percent) if order.percent else '',
                str(order.amount) if order.amount else '', str(order.total_amount) if order.total_amount else '',
                str(order.used_points) if order.used_points else '', str(order.used_cashback) if order.used_cashback else '',
                str (order.hash) if order.hash else '', str (order.commission) if order.commission else '',
                str (order.cashback) if order.cashback else '', str (order.profit) if order.profit else '',
                str (order.referrer) if order.referrer else '', str (order.add_ref_points) if order.add_ref_points else '',
                str(order.add_cashback) if order.add_cashback else ''
            ]
        ]
        sh.sheet1.update(range_name=cell, values=new_row_str)

        return last_row

    except Exception as ex:
        log_error(ex)


# обновляет статус
def update_status_ggl(status: str, row: int) -> None:
    sh = get_google_connect()

    try:
        cell = f'C{row}'
        new_row_str = [
            [status]
        ]
        sh.sheet1.update(range_name=cell, values=new_row_str)

    except Exception as ex:
        log_error(ex)