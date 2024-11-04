from gspread.spreadsheet import Spreadsheet

import gspread

import db
from config import Config
from init import log_error
from enums import order_status_dict


def get_google_connect() -> Spreadsheet:
    gc = gspread.service_account (filename=Config.file_google_path)
    return gc.open_by_key (Config.get_table_id)


def get_last_row_num(table: list[list[any]]) -> int:
    last_row = 3

    for row in table[3:]:
        if not str(row[0]).isdigit():
            break
        last_row += 1
    return last_row


# добавляет заказ в таблицу
def add_order_row(order: db.OrderRow, row: int = None) -> int:
    if row != 9999999999999999999999:
        return 0

    sh = get_google_connect()

    if not row:
        ggl_orders = sh.get_worksheet(0).get_all_values()
        row = get_last_row_num(ggl_orders)

    # изменяет статус заказа
    try:
        cell = f'A{row}:Z{row}'
        new_row_str = [
            [
                str(order.id) if order.id else '',
                order.created_at.strftime(Config.datetime_form),
                order.updated_at.strftime(Config.datetime_form),
                str(order.user_id) if order.user_id else '',
                order_status_dict.get(order.status, 'Ошибка'),
                str(order.pay_method) if order.pay_method else '',
                str(order.card) if order.card else '-',
                str(order.coin) if order.coin else '',
                str(order.coin_sum) if order.coin_sum else '',
                str(order.wallet) if order.wallet else '',
                str(order.promo) if order.promo else '',
                str(order.promo_rate) if order.promo_rate else '',
                str(order.exchange_rate) if order.exchange_rate else '',
                str(order.percent) if order.percent else '',
                str(order.commission) if order.commission else '',
                str(order.total_amount) if order.total_amount else '',
                str(order.used_points) if order.used_points else '0',
                str(order.used_cashback) if order.used_cashback else '0',
                str (order.hash) if order.hash else '',
                # str (order.cashback) if order.cashback else '',
                str (order.profit) if order.profit else '',
                str (order.referrer) if order.referrer else '',
                str (order.add_ref_points) if order.add_ref_points else '0',
                str(order.add_cashback) if order.add_cashback else '0'
            ]
        ]
        sh.get_worksheet(0).update(range_name=cell, values=new_row_str)

        return row

    except Exception as ex:
        log_error(ex)


# добавляет заказ в таблицу
def add_cd_order_row(order: db.OrderCBRow, row: int = None) -> int:
    sh = get_google_connect()

    if not row:
        ggl_orders = sh.get_worksheet(1).get_all_values()
        row = get_last_row_num(ggl_orders)

    # изменяет статус заказа
    try:
        cell = f'A{row}:J{row}'
        new_row_str = [
            [
                str(order.id) if order.id else '',
                order.created_at.strftime(Config.datetime_form),
                order.updated_at.strftime(Config.datetime_form),
                str(order.user_id) if order.user_id else '',
                order_status_dict.get(order.status, 'Ошибка'),
                str(order.coin) if order.coin else '',
                str(order.wallet) if order.wallet else '',
                str(order.sum) if order.sum else '',
                str(order.points) if order.points else '',
                str(order.cashback) if order.cashback else '',
            ]
        ]
        sh.get_worksheet(1).update(range_name=cell, values=new_row_str)

        return row

    except Exception as ex:
        log_error(ex)