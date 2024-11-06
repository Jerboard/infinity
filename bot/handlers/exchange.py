from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter

from asyncio import sleep
from datetime import datetime

import db
import keyboards as kb
from config import Config
from init import dp, bot
import utils as ut
from enums import CB, Key, UserStatus, Action, OrderStatus, MainButton


# продать старт инлайн
@dp.callback_query(lambda cb: cb.data.startswith(CB.SELL.value))
async def russian_rub_inline(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await ut.russian_rub(cb.message, edit_msg=cb.message.message_id)


# старт обмена инлайн
@dp.callback_query(lambda cb: cb.data.startswith(CB.EXCHANGE.value))
async def select_currency_inline(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await ut.select_currency(cb.message, state, edit_msg=cb.message.message_id)


# выбор способа оплаты
@dp.callback_query(lambda cb: cb.data.startswith(CB.SELECT_PAYMENT.value))
async def send_sum(cb: CallbackQuery, state: FSMContext):
    _, currency_id_str = cb.data.split(':')

    if currency_id_str != 'back':
        currency_id = int(currency_id_str)
        currency = await db.get_currency(currency_id=currency_id)
        currency_name = f'{currency.name} ({currency.code})'
        await state.update_data(data={
            'user_id': cb.from_user.id,
            'currency_id': currency.id,
            'currency_name': currency_name,
            'message_id': cb.message.message_id
        })

    else:
        await state.update_data(data={'back': True})
        data = await state.get_data()
        currency = await db.get_currency(currency_id=data['currency_id'])
        currency_name = data['currency_name']

    min_sum = currency.min if currency.min != 0 else 'Без ограничения'
    msg_key = ut.get_send_sum_key(currency.code)
    msg_data = await db.get_msg(msg_key)
    text = msg_data.text.format(
        currency_name=currency_name,
        min_sum=min_sum,
        min_sum_str=str(min_sum).replace(".", ",")
    )
    # text = (f'Введите нужную сумму в {currency_name} или в рублях (RUB) Пример: {min_sum} или {min_sum_str} или 5000\n\n')

    await state.set_state(UserStatus.EXCHANGE_SEND_SUM)
    await ut.send_msg(
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        msg_data=msg_data,
        text=text,
        keyboard=kb.get_cancel_kb()
        # keyboard=kb.get_back_kb(CB.EXCHANGE.value)
    )


# приём суммы монеты и калькулятор
@dp.message(StateFilter(UserStatus.EXCHANGE_SEND_SUM))
async def sum_exchange(msg: Message, state: FSMContext):
    input_sum = msg.text.replace(',', '.')
    if not ut.is_digit(input_sum):
        sent = await msg.answer('❌ Некорректная сумма')
        await sleep(3)
        await msg.delete()
        await sent.delete()

    else:
        input_sum = float(input_sum)
        data = await state.get_data()

        currency = await db.get_currency(currency_id=data['currency_id'])

        if input_sum <= 200:
            sum_coin = input_sum
            sum_rub = round(sum_coin * currency.rate)
            input_coin = True
        else:
            sum_rub = input_sum
            sum_coin = sum_rub / currency.rate
            input_coin = False

        correct_sum = True
        text = 'Произошла ошибка перезапустите бот /start'

        if sum_coin < currency.min:
            min_rub = round(currency.rate * currency.min)
            text = (f'❌ Некорректная сумма\n'
                    f'Сумма должна быть больше:\n'
                    f'{currency.min} {currency.code}\n'
                    f'{min_rub} руб.')

            correct_sum = False

        elif sum_coin > currency.max:
            max_rub = round(currency.rate * currency.max)
            text = (f'❌ Некорректная сумма\n' 
                    f'Сумма должна быть меньше:\n' 
                    f'{currency.max} {currency.code}\n' 
                    f'{max_rub} руб.')

            correct_sum = False

        # если некорректная сумма - просит новую
        if not correct_sum:
            try:
                await bot.delete_message(chat_id=msg.chat.id, message_id=data['message_id'])
            except TelegramBadRequest as ex:
                pass

            sent = await ut.send_msg(
                msg_key=Key.SEND_SUM.value,
                chat_id=msg.chat.id,
                text=text,
            )
            await state.update_data(data={'message_id': sent.message_id})

        else:
            user_data = await db.get_user_info(msg.from_user.id)
            # balance = user_data.referral_points + user_data.cashback
            promo = await db.get_used_promo(user_id=msg.from_user.id, used=False)
            info = await db.get_info()

            await state.update_data(data={
                'input_sum': msg.text,
                'input_coin': input_coin,
                'start_time': datetime.now(),
                'user_rub_sum': sum_rub,
                'coin_rate': currency.rate,
                'commission': currency.commission,
                'buy_rate': currency.buy_price,
                'percent': currency.ratio,
                'currency_code': currency.code,
                'coin_round': currency.round,
                'cashback_rate': info.cashback,
                'promo_data': promo,
                'used_promo': False,
                'used_balance': False,
                'user_info': user_data,
            })

            await ut.main_exchange(state, del_msg=True)

            # await state.update_data(data={
            #
            #     'referral_points': user_data.referral_points,
            #     'cashback': user_data.cashback,
            #     'used_promo': False,
            #     'promo_data': promo,
            # })

            # if promo:
            #     await state.update_data(data={
            #         'promo_id': promo.id,
            #         'promo_rate': promo.rate,
            #         'promo': promo.promo,
            #     })


# Использовать промо
@dp.callback_query(lambda cb: cb.data.startswith(CB.USE_PROMO.value))
async def use_promo(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if data.get('used_promo'):
        await cb.answer('ПРОМОКОД УЖЕ ПРИМЕНЕН', show_alert=True)
        return

    # promo = await db.get_used_promo(user_id=cb.from_user.id, used=False)
    promo: db.UsedPromoRow = data['promo_data']

    await state.update_data(data={
        'used_promo': True,
        'promo_id': promo.id,
        'promo_rate': promo.rate,
        'promo': promo.promo,
    })
    await ut.main_exchange(state)


# Использовать баллы
@dp.callback_query(lambda cb: cb.data.startswith(CB.USE_CASHBACK.value))
async def use_point(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if data.get('used_balance'):
        await cb.answer('ВНУТРЕННИЙ БАЛАНС КОШЕЛЬКА УЖЕ ПРИМЕНЕН', show_alert=True)
        return

    if data['balance'] == 0:
        await cb.answer('ВНУТРЕННИЙ БАЛАНС КОШЕЛЬКА РАВЕН НУЛЮ', show_alert=True)
        return

    # if data['balance'] > data['total_amount']:
    #     used_balance = data['balance'] - data['total_amount'] + 1
    #     total_amount = 1
    #
    # else:
    #     used_balance = data['balance']
    #     total_amount = data['total_amount'] - data['balance']

    # pay_string = f'<s>{data["pay_string"]}</s>\nК ОПЛАТЕ С УЧЕТОМ БАЛАНСА: {total_amount}р.'

    await state.update_data(data={
        # 'total_amount': total_amount,
        'used_balance': True,
        # 'pay_string': pay_string,
    })
    await ut.main_exchange(state)


# вернуться к
@dp.callback_query(lambda cb: cb.data.startswith(CB.BACK_CHECK_INFO.value))
async def send_wallet(cb: CallbackQuery, state: FSMContext):
    await ut.main_exchange(state)


# выбор кошелька LevL7S8DNFGQWnRrtjzhEJHRcPBMYCLwWC ltc
@dp.callback_query(lambda cb: cb.data.startswith(CB.SEND_WALLET.value))
async def send_wallet(cb: CallbackQuery, state: FSMContext):
    _, method_str = cb.data.split(':')
    pay_method_id = int(method_str)

    data = await state.get_data()
    await state.set_state(UserStatus.EXCHANGE_SEND_WALLET)
    await state.update_data(data={'pay_method_id': pay_method_id})

    msg_data = await db.get_msg(Key.SEND_WALLET.value)

    text = msg_data.text.format(currency_name=data["currency_name"])
    await ut.send_msg(
        msg_data=msg_data,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_cancel_kb()
        # keyboard=kb.get_back_kb(CB.BACK_CHECK_INFO.value)
    )


# приём номера кошелька и проверка его
@dp.message(StateFilter(UserStatus.EXCHANGE_SEND_WALLET))
async def check_wallet(msg: Message, state: FSMContext):
    # await msg.delete()

    data = await state.get_data()

    if not ut.check_valid_wallet(coin=data['currency_code'], wallet=msg.text):
        # await msg.answer('❌ Некорректный адрес кошелька')

        # text = f'<b>Укажи {data["currency_name"]}-Кошелек:</b>'
        await ut.send_time_message(chat_id=msg.chat.id, text='❌ Некорректный адрес кошелька', msg_ids=[msg.message_id])
        # await sleep(3)
        # await msg.delete()
        # await ut.send_msg(
        #     msg_key=Key.SEND_WALLET.value,
        #     chat_id=msg.chat.id,
        #     # edit_msg=data['message_id'],
        #     text=text,
        #     keyboard=kb.get_cancel_kb()
        # )
        return

    # checked_wallet = await db.get_wallet(code=data['currency_code'], wallet=msg.text)
    # if not checked_wallet:
    #     check = await ut.check_wallet(coin_code=data['currency_code'], wallet=msg.text)
    #     if check:
    #         if not Config.debug:
    #             await db.add_wallet(user_id=msg.from_user.id, code=data['currency_code'], wallet=msg.text)
    #
    #     else:
    #         await msg.answer('❌ Некорректный адрес кошелька')
    #
    #         text = f'<b>Укажи {data["currency_name"]}-Кошелек:</b>'
    #         await ut.send_msg(
    #             msg_key=Key.SEND_WALLET.value,
    #             chat_id=msg.chat.id,
    #             edit_msg=data['message_id'],
    #             text=text,
    #             keyboard=kb.get_back_kb(CB.SELECT_PAYMENT.value)
    #         )
    #         return

    await state.update_data(data={'wallet': msg.text})

    if data.get('promo_id'):
        await db.update_used_promo(promo_id=data['promo_id'], used=True)

    # списываем баллы
    use_points, use_cashback = 0, 0
    if data.get('used_balance'):
        # if data['total_amount'] == 1:
        #     use_points = data['referral_points']
        #     use_cashback = data['used_balance'] - data['referral_points']
        #
        # else:
        #     use_points = data['referral_points']
        #     use_cashback = data['cashback']

        await db.update_user_info(
            user_id=msg.from_user.id,
            add_point=0 - data['use_points'],
            add_cashback=0 - data['use_cashback']
        )

    # for k, v in data.items():
    #     print(f'{k}:{v}')

    await state.clear()
    pay_method_info = await db.get_pay_method(data['pay_method_id'])
    order_id = await db.add_order(
        user_id=msg.from_user.id,
        coin=data['currency_code'],
        pay_method=pay_method_info.name,
        card=pay_method_info.card,
        coin_sum=data['coin_sum'],
        wallet=msg.text,
        promo=data.get('promo'),
        promo_rate=data.get('promo_rate', 0),
        exchange_rate=data['coin_rate'],
        percent=data['percent'],
        amount=data['amount'],
        used_points=data['use_points'],
        used_cashback=data['use_cashback'],
        total_amount=data['total_amount'],
        message_id=data['message_id'],
        promo_used_id=data.get('promo_id', 0),
        commission=data['commission'],
        profit=data['profit'],
        cashback=data['cashback']
    )

    msg_data = await db.get_msg(Key.PAYMENT.value)
    text = msg_data.text.format(
        pay_method_name=pay_method_info.name,
        pay_method_card=pay_method_info.card,
        total_amount=data["total_amount"],
        order_id=order_id
    )

    await bot.delete_message(chat_id=msg.from_user.id, message_id=data['message_id'])
    sent = await ut.send_msg(
        msg_data=msg_data,
        chat_id=msg.chat.id,
        text=text,
        keyboard=kb.get_payment_conf_kb(order_id)
    )
    await state.clear()

    # добавляем в таблицу
    order = await db.get_order(order_id)
    row = ut.add_order_row(order)
    await db.update_order(order_id=order_id, row=row)


# ожидание оплаты
@dp.callback_query(lambda cb: cb.data.startswith(CB.PAYMENT_CONF.value))
async def payment_conf(cb: CallbackQuery, state: FSMContext):
    _, order_str, action = cb.data.split(':')
    order_id = int(order_str)

    if action == Action.DEL:
        order = await db.get_order(order_id)
        await ut.del_order(order)

    else:
        await db.update_order(order_id=order_id, status=OrderStatus.NEW.value)
        order = await db.get_order(order_id)

        msg_data = await db.get_msg(Key.PAYMENT_CONF.value)
        text = msg_data.text.format(
            order_id=order_id,
            total_amount=order.total_amount
        )

        await ut.send_msg(
            msg_data=msg_data,
            chat_id=cb.message.chat.id,
            edit_msg=cb.message.message_id,
            text=text
        )

        # ut.add_order_row(order=order, row=order.row)

        username = f'@{cb.from_user.username}' if cb.from_user.username is not None else ''
        text = f'<b>Новая заявка:</b>\n' \
               f'<b>Номер заявки:</b> {order_id}\n' \
               f'<b>От:</b> {cb.from_user.full_name} {username}\n' \
               f'<b>Валюта:</b> {order.coin}\n' \
               f'<b>Сумма валюты:</b> <code>{order.coin_sum}</code>\n' \
               f'<b>На кошелёк:</b> <code>{order.wallet}</code>\n' \
               f'<b>Перевод на:</b> {order.pay_method}\n' \
               f'<b>Сумма рублей:</b> <code>{order.total_amount}</code>'

        await bot.send_message(Config.access_chat, text)
