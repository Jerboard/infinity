from random import choice

import db
from config import Config
import utils as ut
from enums import Coin, Key, InputType


# проверяет на цифру
def is_digit(text):
    try:
        float(text)
        return True
    except:
        return False


# возвращает нужный ключ для обмена
def get_send_sum_key(coin: str) -> str:
    if coin == Coin.BTC:
        return Key.SEND_SUM_BTC.value
    elif coin == Coin.LTC:
        return Key.SEND_SUM_LTC.value
    elif coin == Coin.XMR:
        return Key.SEND_SUM_XMR.value
    else:
        return Key.SEND_SUM_USDT.value


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


# считает сумму к аплате профит и прочие, списывает
def amount_calculator(
        coin_rate: int,
        # user_rub_sum: int,
        input_sum: int,
        input_type: str,
        commission: int,
        infinity_percent: float,
        coin_round: int,
        buy_rate: int,
        cashback_rate: float,
        user_info: db.UserRow,
        promo_rate: int = None,
        used_balance: bool = None
) -> dict:
    if input_type == InputType.COIN:
        coin_sum = input_sum
        rub_sum = input_sum * coin_rate
    else:
        coin_sum = input_sum / coin_rate
        rub_sum = input_sum

    infinity_rate = coin_rate * ((infinity_percent / 100) + 1)  # курс рынка
    amount = (coin_sum * infinity_rate) + commission  # сумма с пользователя
    total_amount = amount
    buy_rate = buy_rate or 0
    profit = (coin_sum * infinity_rate) - (coin_sum * buy_rate)  # прибыль

    pay_string = f'📍 К ОПЛАТЕ {round(total_amount)} RUB 📍'

    if promo_rate:
        discount = profit * (promo_rate / 100)
        total_amount -= discount
        profit -= discount

        pay_string = f'<s>{pay_string.replace("📍", "")}</s>\n📍 К ОПЛАТЕ С УЧЕТОМ ПРОМОКОДА: {round(total_amount)} р. 📍'

    else:
        discount = 0

    # print(f'cashback: {user_info.cashback} referral_points: {user_info.referral_points}')
    # cashback: 5 referral_points: 1000
    balance = user_info.cashback + user_info.referral_points
    use_points, use_cashback = 0, 0
    if used_balance:
        if total_amount > balance:
            use_cashback = user_info.cashback
            use_points = user_info.referral_points
            total_amount -= balance
            profit -= balance

        else:
            if user_info.referral_points < total_amount:
                use_points = user_info.referral_points
                use_cashback = total_amount - use_points - 1

            elif user_info.referral_points == total_amount:
                use_points = user_info.referral_points - 1
                use_cashback = 0

            else:
                use_points = total_amount - 1
                use_cashback = 0

            total_amount = 1
            profit -= (use_points + use_cashback)

        if profit < 0:
            profit = 0

        pay_string = f'<s>{pay_string.replace("📍", "")}</s>\n📍 К ОПЛАТЕ С УЧЕТОМ БАЛАНСА: {round(total_amount)}р. 📍'

    if profit > 0:
        cashback = profit * (cashback_rate / 100)
    else:
        cashback = 0

    return {
        'coin_sum': round(coin_sum, coin_round),
        'rub_sum': round(rub_sum),
        'total_amount': round(total_amount),
        'amount': round(amount),
        'profit': round(profit),
        'cashback': round(cashback),
        'discount': round(discount),
        'pay_string': pay_string,
        'balance': round(balance),
        'use_points': round(use_points),
        'use_cashback': round(use_cashback),
    }



'''
user_coin_sum: 0.8333333333333334
commission_rate: 1.1
infinity_rate: 6600.000000000001
amount: 5510.000000000001
profit: 250.0000000000009
cashback: 3

Курс рынка = 6000р (за 1 монету (LTC))
Комиссия сервиса = 10%
Комиссия за отправку = 10р
Курс закупа = 6300р

Обмен на 5000р, баланс на 100р и 500р: (2 примера)
Кол-во монет = 0.8333 монет
курс рынка (6000) + комиссия сервиса 10% = 6600 * на сумму обмена в крипте (0.8333 ltc по курсу) = 5500 + 10р (комиссия сервиса за отправку) = 5510 к оплате без учета баланса
прибыль бот может рассчитать умножив 0.8333 лтс на курс продажи (курс рынка + комиссия сервиса 6600) - 0.833 лтс * на (курс закупа 6300) = прибыль равняется 253
То есть 0.8333 * 6600 - 0.8333 * 6300 = 5500-5247 = 253 прибыль

То есть пользователь сделал обмен на 5000, бот рассчитал, что к оплате нужно 5510 и прибыль составляет 253р. 
Он использует 100 баллов и получается 5510-100=5410 к оплате
и прибыль уменьшилась на 100 (253-100)= 153 новое значение прибыли. 
кешбек и реферальные отчисления будут считаться от 153р

Рассмотрим случай, когда значение баланса выше чем прибыль с обмена. 
Клиент меняет также на 5000 бот рассчитал, что к оплате нужно 5510 и прибыль составляет 253р. 
Он использует 500 баллов и получается 5510-500=5010 к оплате 
(баллы минусовать в таком случае и всю прибыль и отсаток с основного тела депозита, !!! 
Проговорить на созвоне !!!). Прибыль в данном случае отрицательная (253-500=-247)
(Если сумма списанного баланса >= Прибыли, то кэшбэк = 0р.)
Если клиент является рефералом, то владельцу реферала должен быть начислен процент от 153р прибыли в зависимости от уровня рефералки.
(Если сумма списанного баланса >= Прибыли, то сумма начисления по рефералке = 0р.)
'''