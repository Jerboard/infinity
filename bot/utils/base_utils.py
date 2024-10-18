from random import choice

import db


# проверяет на цифру
def is_digit(text):
    try:
        float(text)
        return True
    except:
        return False


#   считает прибыль с обмена
def get_profit_exchange(coin_sum: float, buy_price: float, total_amount: float, commission: float) -> int:
    buy_price = coin_sum * buy_price
    profit = round((total_amount - commission) - buy_price)
    return 0 if profit < 0 else profit


def get_check_info_text(data: dict, currency: db.CurrencyRow) -> str:
    if data.get('promo') or data.get('used_points'):
        text = f'<i>Курс покупки <b>{currency.name}</b> {data["rate"]} руб\n\n' \
               f'<b>К оплате:</b> <s>{data["amount"]} руб.</s>\n' \
               f'<b>С учетом скидки:</b> {data["total_amount"]} руб.\n' \
               f'<b>К получению:</b> {data["sum_exchange"]} {currency.code}\n' \
               f'<b>На кошелек:</b> {data["wallet"]}\n' \
               f'<b>Время обмена:</b> От 5 до 60 мин.\n\n' \
               f'Если вы согласны с условием обмена, нажмите <b>“Все верно” </b></i>'

    else:
        text = f'<i>Курс покупки <b>{currency.name}</b> {data.get("rate")} руб\n\n' \
               f'<b>К оплате:</b> {data["amount"]} руб.\n' \
               f'<b>К получению:</b> {data["sum_exchange"]} {currency.code}\n' \
               f'<b>На кошелек:</b> {data["wallet"]}\n' \
               f'<b>Время обмена:</b> От 5 до 60 мин.\n\n' \
               f'Если вы согласны с условием обмена, нажмите <b>“Все верно” </b></i>'

    return text
