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
from enums import CB, Key, UserStatus, Action, OrderStatus


# кнопка продать
@dp.callback_query(lambda cb: cb.data.startswith(CB.SELL.value))
async def russian_rub(cb: CallbackQuery):
    # text = 'Продажа валюты через оператора'
    await ut.send_msg(
        msg_key=Key.SELL.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        # text=text,
        keyboard=kb.get_sell_kb()
    )


# выбор валюты
# @dp.message(text=['✅ Купить'], state='*')
@dp.callback_query(lambda cb: cb.data.startswith(CB.EXCHANGE.value))
async def select_currency(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    check_orders = await db.get_orders(user_id=cb.from_user.id, check=True)

    if check_orders:
        text = 'У вас ещё осталась незакрытая заявка'
        # await cb.message.answer(text)
        await ut.send_time_message(chat_id=cb.message.chat.id, text=text)
    else:
        await state.set_state(UserStatus.EXCHANGE)

        # text = 'Выберите валюту, которую хотите получить '
        currency = await db.get_all_currency()
        await ut.send_msg(
            msg_key=Key.SELECT_CURRENCY.value,
            chat_id=cb.message.chat.id,
            edit_msg=cb.message.message_id,
            # text=text,
            keyboard=kb.get_currency_list_kb(currency)
        )


# выбор способа оплаты
@dp.callback_query(lambda cb: cb.data.startswith(CB.SELECT_PAYMENT.value))
async def send_sum(cb: CallbackQuery, state: FSMContext):
    _, currency_id_str = cb.data.split(':')

    if currency_id_str != 'back':
        currency_id = int(currency_id_str)
        currency = await db.get_currency(currency_id)
        currency_name = f'{currency.name} ({currency.code})'
        await state.update_data(data={
            'user_id': cb.from_user.id,
            'currency_id': currency.id,
            'currency_name': currency_name,
            'message_id': cb.message.message_id
        })

    else:
        data = await state.get_data()
        currency = await db.get_currency(data['currency_id'])
        currency_name = data['currency_name']

    min_sum = currency.min if currency.min != 0 else 'Без ограничения'
    msg_data = await db.get_msg(Key.SEND_SUM.value)
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
        keyboard=kb.get_back_kb(CB.EXCHANGE.value)
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
        # await state.set_state('exchange_send_sum')

        currency = await db.get_currency(data['currency_id'])

        # зачем тут +1
        currency_rate = round(currency.rate * ((currency.ratio / 100) + 1))

        # if input_sum <= currency.max:
        if input_sum <= 200:
            sum_coin = input_sum
            sum_rub = round(sum_coin * currency_rate)
            total_amount = sum_rub + currency.commission
            # sum_rub = round((sum_coin * currency_rate))
        else:
            sum_rub = input_sum
            sum_coin = sum_rub / currency_rate
            total_amount = sum_rub + currency.commission
            # sum_coin = (sum_rub - currency.commission) / currency_rate

        correct_sum = True
        text = 'Произошла ошибка перезапустите бот /start'
        if sum_coin < currency.min:
            min_rub = round(currency_rate * currency.min)
            text = (f'❌ Некорректная сумма\n'
                    f'Сумма должна быть больше:\n'
                    f'{currency.min} {currency.code}\n'
                    f'{min_rub} руб.')

            correct_sum = False

        elif sum_coin > currency.max:
            max_rub = round(currency_rate * currency.max)
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
                msg_key=Key.SUM_EXCHANGE.value,
                chat_id=msg.chat.id,
                text=text,
            )
            await state.update_data(data={'message_id': sent.message_id})

        else:
            user_data = await db.get_user_info(msg.from_user.id)
            print(f'user_data:{user_data}')
            # balance = user_data.referral_points + user_data.cashback

            sum_coin = round(sum_coin, currency.round)
            await state.update_data(data={
                'amount': sum_rub,
                'total_amount': total_amount,
                'sum_exchange': sum_coin,
                'rate': currency_rate,
                'start_time': datetime.now(),
                'commission': currency.commission,
                'percent': currency.ratio,
                'balance': user_data.referral_points + user_data.cashback,
                'referral_points': user_data.referral_points,
                'cashback': user_data.cashback,
                'currency_code': currency.code,
                'pay_string': f'К ОПЛАТЕ {total_amount}Р',
            })
            promo = await db.get_used_promo(user_id=msg.from_user.id)
            if promo:
                await state.update_data(data={
                    'promo_id': promo.id,
                    'promo_rate': promo.rate,
                    'promo': promo.promo,
                })

            await ut.main_exchange(state, del_msg=True)


# Использовать промо
@dp.callback_query(lambda cb: cb.data.startswith(CB.USE_PROMO.value))
async def use_promo(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if data.get('used_promo'):
        await cb.answer('ПРОМОКОД УЖЕ ПРИМЕНЕН', show_alert=True)
        return

    rate = 1 - (data['promo_rate'] / 100)
    total_amount = round(data['total_amount'] * rate)

    pay_string = f'<s>{data["pay_string"]}</s>\nК ОПЛАТЕ С УЧЕТОМ ПРОМОКОДА: {total_amount}р.'

    await state.update_data(data={
        'total_amount': total_amount,
        'pay_string': pay_string,
        'used_promo': True,
    })
    await ut.main_exchange(state)


# Использовать баллы
@dp.callback_query(lambda cb: cb.data.startswith(CB.USE_CASHBACK.value))
async def use_point(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if data.get('used_balance'):
        await cb.answer('ВНУТРЕННИЙ БАЛАНС КОШЕЛЬКА УЖЕ ПРИМЕНЕН', show_alert=True)
        return

    if data['balance'] > data['total_amount']:
        used_balance = data['balance'] - data['total_amount'] + 1
        total_amount = 1

    else:
        used_balance = data['balance']
        total_amount = data['total_amount'] - data['balance']

    pay_string = f'<s>{data["pay_string"]}</s>\nК ОПЛАТЕ С УЧЕТОМ БАЛАНСА: {total_amount}р.'

    await state.update_data(data={
        'total_amount': total_amount,
        'used_balance': used_balance,
        'pay_string': pay_string,
    })
    await ut.main_exchange(state)


# выбор кошелька LevL7S8DNFGQWnRrtjzhEJHRcPBMYCLwWC ltc
@dp.callback_query(lambda cb: cb.data.startswith(CB.SEND_WALLET.value))
async def send_wallet(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(UserStatus.EXCHANGE_SEND_WALLET)
    msg_data = await db.get_msg(Key.SEND_WALLET.value)

    text = msg_data.text.format(currency_name=data["currency_name"])
    await ut.send_msg(
        msg_data=msg_data,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_back_kb(CB.SELECT_PAYMENT.value)
    )


# приём номера кошелька и проверка его
@dp.message(StateFilter(UserStatus.EXCHANGE_SEND_WALLET))
async def check_wallet(msg: Message, state: FSMContext):
    # await msg.delete()

    data = await state.get_data()
    checked_wallet = await db.get_wallet(code=data['currency_code'], wallet=msg.text)
    if not checked_wallet:
        check = await ut.check_wallet(coin_code=data['currency_code'], wallet=msg.text)
        if check:
            if not Config.debug:
                await db.add_wallet(user_id=msg.from_user.id, code=data['currency_code'], wallet=msg.text)

        else:
            await msg.answer('❌ Некорректный адрес кошелька')

            text = f'<b>Укажи {data["currency_name"]}-Кошелек:</b>'
            await ut.send_msg(
                msg_key=Key.SEND_WALLET.value,
                chat_id=msg.chat.id,
                edit_msg=data['message_id'],
                text=text,
                keyboard=kb.get_back_kb(CB.SELECT_PAYMENT.value)
            )
            return

    await state.update_data(data={'wallet': msg.text})

    if data.get('promo_id'):
        await db.update_used_promo(promo_id=data['promo_id'], used=True)

    # списываем баллы
    use_points, use_cashback = 0, 0
    if data.get('used_points'):
        if data['total_amount'] == 1:
            use_points = data['referral_points']
            use_cashback = data['used_balance'] - data['referral_points']

        else:
            use_points = data['referral_points']
            use_cashback = data['cashback']

        await db.update_user_info(
            user_id=msg.from_user.id,
            add_point=0 - use_points,
            add_cashback=0 - use_cashback
        )

    pay_method_info = await db.get_pay_method()
    order_id = await db.add_order(
        user_id=msg.from_user.id,
        coin=data['currency_code'],
        pay_method=pay_method_info.name,
        coin_sum=data['sum_exchange'],
        # wallet=data['wallet'],
        wallet=msg.text,
        promo=data.get('promo'),
        promo_rate=data.get('promo_rate', 0),
        exchange_rate=data['rate'],
        percent=data['percent'],
        amount=data['amount'],
        used_points=use_points,
        used_cashback=use_cashback,
        total_amount=data['total_amount'],
        message_id=data['message_id'],
        promo_used_id=data.get('promo_id', 0),
        commission=data['commission'],
    )

    await state.update_data(data={'order_id': order_id})

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

    await state.update_data(data={'message_id': sent.message_id, 'pay_method': pay_method_info.card})


# ожидание оплаты
@dp.callback_query(lambda cb: cb.data.startswith(CB.PAYMENT_CONF.value))
async def payment_conf(cb: CallbackQuery, state: FSMContext):
    _, order_str, action = cb.data.split(':')
    order_id = int(order_str)

    data = await state.get_data()
    await state.clear()
    # for k, v in data.items():
    #     print(f'{k}: {v}')

    if action == Action.DEL:
        order = await db.get_order(order_id)
        await ut.del_order(order)

    else:
        await db.update_orders(order_id=order_id, status=OrderStatus.NEW.value)
        msg_data = await db.get_msg(Key.PAYMENT_CONF.value)
        text = msg_data.text.format(
            order_id=order_id,
            total_amount=data["total_amount"]
        )

        await ut.send_msg(
            msg_data=msg_data,
            chat_id=cb.message.chat.id,
            edit_msg=cb.message.message_id,
            text=text
        )

        username = f'@{cb.from_user.username}' if cb.from_user.username is not None else ''
        text = f'<b>Новая заявка:</b>\n' \
               f'<b>Номер заявки:</b> {order_id}\n' \
               f'<b>От:</b> {cb.from_user.full_name} {username}\n' \
               f'<b>Валюта:</b> {data["currency_name"]}\n' \
               f'<b>Сумма валюты:</b> <code>{data["sum_exchange"]}</code>\n' \
               f'<b>На кошелёк:</b> <code>{data["wallet"]}</code>\n' \
               f'<b>Перевод на:</b> {data["pay_method"]}\n' \
               f'<b>Сумма рублей:</b> <code>{data["total_amount"]}</code>'

        await bot.send_message(Config.access_chat, text)







# назад к чекинфо
# @dp.callback_query(lambda cb: cb.data.startswith(CB.BACK_CHECK_INFO.value))
# async def back_check_info(cb: CallbackQuery, state: FSMContext):
#     await ut.check_info_output(state)


# Введите промокод
# @dp.callback_query(lambda cb: cb.data.startswith(CB.USE_PROMO.value))
# async def add_promo(cb: CallbackQuery, state: FSMContext):
#     await state.set_state(UserStatus.EXCHANGE_SEND_PROMO)
#     text = f'<b>Введите промокод на скидку</b>'
#
#     await ut.send_msg(
#         msg_key=Key.ADD_PROMO.value,
#         chat_id=cb.message.chat.id,
#         edit_msg=cb.message.message_id,
#         text=text,
#         keyboard=kb.get_back_kb(CB.BACK_CHECK_INFO.value)
#     )


# приём номера кошелька и проверка его с учётом промокода
# @dp.message(StateFilter(UserStatus.EXCHANGE_SEND_PROMO))
# async def check_info_promo(msg: Message, state: FSMContext):
#     await msg.delete()
#     data = await state.get_data()
#
#     promo_data = await db.get_promo(msg.text)
#     if not promo_data:
#         sent = await msg.answer('❌ Неверный промокод')
#         await sleep(3)
#         await bot.delete_message(sent.chat.id, sent.message_id)
#         return
#
#     used_promo = await db.get_used_promo(promo=msg.text, user_id=msg.from_user.id)
#
#     if (promo_data.is_onetime and used_promo) or (len(used_promo) >= promo_data.many):
#         sent = await msg.answer('✅ Промокод уже применён')
#         await sleep(3)
#         await bot.delete_message(sent.chat.id, sent.message_id)
#
#     else:
#         promo_amount = data['total_amount'] - promo_data.rate
#         if promo_amount < 1:
#             promo_amount = 1
#
#         # promo_amount = check_unique_amount(promo_amount)
#         await state.update_data(data={
#             'promo': promo_data.promo,
#             'promo_rate': promo_data.rate,
#             # 'promo_used_id': promo_data.promo_used_id,
#             'total_amount': promo_amount
#         })
#
#         await ut.check_info_output(state)


# Использовать баллы
# @dp.callback_query(lambda cb: cb.data.startswith(CB.USE_CASHBACK.value))
# async def use_cashback(cb: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     user = await db.get_user_info(cb.from_user.id)
#
#     if data['total_amount'] > user.balance:
#         total_amount = data['total_amount'] - user.balance
#         used_balance = user.balance
#     else:
#         total_amount = 1
#         used_balance = (user.balance - data['total_amount']) + 1
#
#     # await db.update_user_info(user_id=cb.from_user.id, add_balance=0 - used_balance)
#
#     # total_amount = check_unique_amount(total_amount)
#     # update_balance(cb.from_user.id, return_points)
#
#     await state.update_data(data={
#         'used_points': used_balance,
#         'total_amount': total_amount
#     })
#
#     await ut.check_info_output(state)


# подтверждение суммы
# @dp.callback_query(lambda cb: cb.data.startswith(CB.PAYMENT_ADD.value))
# async def payment(cb: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     currency = await db.get_currency(data['currency_id'])
#
#     # total_amount = check_unique_amount(data['total_amount'])
#
#     # await state.update_data(data={'total_amount': total_amount})
#     data = await state.get_data()
#     # for k, v in data.items():
#     #     print(f'{k}: {v}')
#
#     if data.get('promo'):
#         promo_used_id = await db.add_used_promo(user_id=cb.from_user.id, promo=data['promo'])
#     else:
#         promo_used_id = 0
#
#     order_id = await db.add_order(
#         user_id=cb.from_user.id,
#         coin=currency.code,
#         pay_method=data['pay_method'],
#         coin_sum=data['sum_exchange'],
#         wallet=data['wallet'],
#         promo=data.get('promo'),
#         promo_rate=data.get('promo_rate', 0),
#         exchange_rate=data['rate'],
#         percent=data['percent'],
#         amount=data['amount'],
#         used_points=data.get('used_point', 0),
#         total_amount=data['total_amount'],
#         message_id=cb.message.message_id,
#         promo_used_id=promo_used_id,
#         commission=data['commission'],
#     )
#     # списываем баллы
#     if data.get('used_points'):
#         await db.update_user_info(user_id=cb.from_user.id, add_balance=0 - data['used_points'])
#
#     pay_method_info = await db.get_pay_method(method_id=data['pay_method_id'])
#     await state.update_data(data={'order_id': order_id})
#
#     await cb.answer(
#         text='При переводе денег не на тот банк - возврат невозможен. '
#              'По остальным вопросам претензии принимаются в течение 24 часов.',
#         show_alert=True
#     )
#
#     text = f'<b>Номер заявки</b> {order_id}\n' \
#            f'<b>Перевод на:</b> {data["pay_method"]}\n' \
#            f'<b>Номер карты:</b> <code>{pay_method_info.card}</code>\n' \
#            f'<b>Сумма:</b> {data["total_amount"]} RUB\n\n' \
#            f'<b>Важно:</b> Сумма должна быть точной, иначе заявка не будет выполнена и вы потеряете средства. ' \
#            f'Все претензии по обмену принимаются в течении 24 часов.\n\n' \
#            f'<b>ВАЖНО, ПЕРЕВОД СТРОГО НА УКАЗАННЫЙ БАНК, ИНАЧЕ ВЫ ПОТЕРЯЕТЕ СВОИ СРЕДСТВА!</b>'
#
#     await ut.send_msg(
#         msg_key=Key.PAYMENT.value,
#         chat_id=cb.message.chat.id,
#         edit_msg=cb.message.message_id,
#         text=text,
#         keyboard=kb.get_payment_conf_kb(order_id)
#     )


# # ожидание оплаты
# @dp.callback_query(lambda cb: cb.data.startswith(CB.PAYMENT_CONF.value))
# async def payment_conf(cb: CallbackQuery, state: FSMContext):
#     _, order_str, action = cb.data.split(':')
#     order_id = int(order_str)
#
#     data = await state.get_data()
#     await state.clear()
#     # for k, v in data.items():
#     #     print(f'{k}: {v}')
#
#     if action == Action.DEL:
#         order = await db.get_order(order_id)
#         await ut.del_order(order)
#
#     else:
#         await db.update_orders(order_id=order_id, status=OrderStatus.NEW.value)
#
#         text = f'Заявка номер {order_id}\n\n' \
#                f'Статус: Обрабатывается\n' \
#                f'Сумма внесения: {data["total_amount"]} RUB'
#
#         await ut.send_msg(
#             msg_key=Key.PAYMENT_CONF.value,
#             chat_id=cb.message.chat.id,
#             edit_msg=cb.message.message_id,
#             text=text
#         )
#
#         username = f'@{cb.from_user.username}' if cb.from_user.username is not None else ''
#         text = f'<b>Новая заявка:</b>\n' \
#                f'<b>Номер заявки:</b> {order_id}\n' \
#                f'<b>От:</b> {cb.from_user.full_name} {username}\n' \
#                f'<b>Валюта:</b> {data["currency_name"]}\n' \
#                f'<b>Сумма валюты:</b> <code>{data["sum_exchange"]}</code>\n' \
#                f'<b>На кошелёк:</b> <code>{data["wallet"]}</code>\n' \
#                f'<b>Перевод на:</b> {data["pay_method"]}\n' \
#                f'<b>Сумма рублей:</b> <code>{data["total_amount"]}</code>'
#
#         await bot.send_message(Config.access_chat, text)



