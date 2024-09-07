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
from functions.async_utilits import del_order
from enums import CB, Key, UserStatus, Action, OrderStatus


# кнопка продать
# @dp.callback_query(text=['⭕️ Продать'], state='*')
# @dp.callback_query(lambda cb: cb.data.startswith(CB.EXCHANGE.value))
# async def russian_rub(msg: Message):
#     user = await db.get_user_info(msg.from_user.id)
#
#     text = '<b>Если вы хотите продать валюту обратитесь к нашему оператору</b>'
#     photo_id = photos['sell']
#     await msg.answer_photo(photo_id, text, reply_markup=kb.get_sell_rub_kb())


# выбор валюты
# @dp.message(text=['✅ Купить'], state='*')
@dp.callback_query(lambda cb: cb.data.startswith(CB.EXCHANGE.value))
async def select_currency(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    check_orders = await db.get_orders(user_id=cb.from_user.id, check=True)

    if check_orders:
        text = 'У вас ещё осталась незакрытая заявка'
        await cb.message.answer(text)
    else:
        await state.set_state(UserStatus.EXCHANGE)

        text = '🔄Выберите валюту, которую хотите получить'
        currency = await db.get_all_currency()
        await ut.send_msg(
            msg_key=Key.SELECT_CURRENCY.value,
            chat_id=cb.message.chat.id,
            edit_msg=cb.message.message_id,
            text=text,
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
            'user_id': cb.message.from_user.id,
            'currency_id': currency.id,
            'currency_name': currency_name,
            'message_id': cb.message.message_id
        })

    else:
        data = await state.get_data()
        currency = await db.get_currency(data['currency_id'])
        currency_name = data['currency_name']

    min_sum = currency.min if currency.min != 0 else 'Без ограничения'
    text = (f'💰Введите нужную сумму в {currency_name} или в рублях (RUB)  \n\n'
            f'Пример: {min_sum} или {str(min_sum).replace(".", ",")} или 5000\n\n')

    await state.set_state(UserStatus.EXCHANGE_SEND_SUM)
    await ut.send_msg(
        msg_key=Key.SEND_SUM.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
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

        if input_sum <= currency.max:
            sum_coin = input_sum
            sum_rub = round((sum_coin * currency_rate)) + currency.commission
        else:
            sum_rub = input_sum
            sum_coin = (sum_rub - currency.commission) / currency_rate

        min_rub = round(currency_rate * currency.min)
        max_rub = round(currency_rate * currency.max)

        if sum_coin < currency.min:
            text = (f'❌ Некорректная сумма\n'
                    f'Сумма должна быть больше:\n'
                    f'{currency.min} {currency.code}\n'
                    f'{min_rub} руб.')

            reply_markup = None

        elif sum_coin > currency.max:
            text = f'❌ Некорректная сумма\n' \
                   f'Сумма должна быть меньше:\n' \
                   f'{currency.max} {currency.code}\n' \
                   f'{max_rub} руб.'

            reply_markup = None

        else:
            sum_coin = round(sum_coin, currency.round)
            await state.update_data(data={
                'amount': sum_rub,
                'total_amount': sum_rub,
                'sum_exchange': sum_coin,
                'rate': currency_rate,
                'start_time': datetime.now(),
                'commission': currency.commission
})

            user_data = await db.get_user_info(msg.from_user.id)
            balance = user_data.balance if user_data.balance else 0
            text = f'Средний рыночный курс: {currency_rate} руб.\n\n' \
                   f'Вы получите: {sum_coin} {currency.code}\n\n' \
                   f'Внутренний баланс кошелька: {balance} руб.\n\n' \
                   f'Для продолжения выберите способ оплаты:'

            pay_methods = await db.get_all_pay_method()
            reply_markup = kb.get_pay_method_kb(sum_rub=sum_rub, pay_methods=pay_methods)

        try:
            # await state.update_data(data={'chat_id': sent.chat.id, 'message_id': sent.message_id})

            await ut.send_msg(
                msg_key=Key.SUM_EXCHANGE.value,
                chat_id=msg.chat.id,
                edit_msg=data['chat_id'],
                text=text,
                keyboard=reply_markup
            )

        except TelegramBadRequest as ex:
            pass


# выбор кошелька LevL7S8DNFGQWnRrtjzhEJHRcPBMYCLwWC ltc
@dp.callback_query(lambda cb: cb.data.startswith(CB.SEND_WALLET.value))
async def save_pay_method(cb: CallbackQuery, state: FSMContext):
    _, pay_method_str = cb.data.split(':')

    if pay_method_str != Action.BACK:
        pay_method = await db.get_pay_method(method_id=int(pay_method_str))
        await state.update_data(data={
            'pay_method': pay_method.name,
            'pay_method_id': pay_method.id})

    data = await state.get_data()
    await state.set_state(UserStatus.EXCHANGE_SEND_WALLET)

    text = f'<b>Укажи {data["currency_name"]}-Кошелек:</b>'
    await ut.send_msg(
        msg_key=Key.SAVE_PAY_METHOD.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.chat.id,
        text=text,
        keyboard=kb.get_back_kb(CB.SELECT_PAYMENT.value)
    )


# ===========================================================================================
# считает сумму
async def check_info_output(data: dict):
    currency = await db.get_currency(data['currency_id'])

    text = ut.get_check_info_text(data=data, currency=currency)
    await ut.send_msg(
        msg_key=Key.CHECK_WALLET.value,
        chat_id=data['user_id'],
        edit_msg=data['message_id'],
        text=text,
        keyboard=kb.get_check_info_kb(data['use_points'], data['points'], data['promo'])
    )


# приём номера кошелька и проверка его
@dp.message(StateFilter(UserStatus.EXCHANGE_SEND_WALLET))
async def check_wallet(msg: Message, state: FSMContext):
    # await msg.delete()

    data = await state.get_data()
    currency = await db.get_currency(data['currency_id'])

    checked_wallet = await db.get_wallet(code=currency.code, wallet=msg.text)
    if not checked_wallet:
        check = await ut.check_wallet(coin_code=currency.code, wallet=msg.text)
        if check:
            await db.add_wallet(user_id=msg.from_user.id, code=currency.code, wallet=msg.text)

        else:
            await msg.answer('❌ Некорректный адрес кошелька')

            text = f'<b>Укажи {data["currency_name"]}-Кошелек:</b>'
            await ut.send_msg(
                msg_key=Key.SAVE_PAY_METHOD.value,
                chat_id=msg.chat.id,
                edit_msg=data['message_id'],
                text=text,
                keyboard=kb.get_back_kb(CB.SELECT_PAYMENT.value)
            )
            return

    user_data = await db.get_user_info(msg.from_user.id)
    # currency = await db.get_currency(data['currency_id'])

    # await state.set_state('exchange')
    await state.update_data(data={
        'wallet': msg.text,
        'use_points': False,
        'points': user_data.balance,
        'user_id': msg.from_user.id
    })
    data = await state.get_data()

    await check_info_output(data)

    # await bot.delete_message(chat_id=msg.from_user.id, message_id=data['message_id'])
    # text = ut.get_check_info_text(data=data, currency=currency)
    # sent = await ut.send_msg(
    #     msg_key=Key.CHECK_WALLET.value,
    #     chat_id=msg.chat.id,
    #     text=text,
    #     keyboard=kb.get_check_info_kb(data['use_points'], data['points'], data['promo'])
    # )
    #
    # await state.update_data(data={'message_id': sent.message_id})


# назад к чекинфо
@dp.callback_query(lambda cb: cb.data.startswith(CB.BACK_CHECK_INFO.value))
async def back_check_info(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await check_info_output(data)


# Введите промокод
@dp.callback_query(lambda cb: cb.data.startswith(CB.ADD_PROMO.value))
async def add_promo(cb: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatus.EXCHANGE_SEND_PROMO)
    text = f'<b>Введите промокод на скидку</b>'

    await ut.send_msg(
        msg_key=Key.ADD_PROMO.value,
        chat_id=cb.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_back_kb(CB.BACK_CHECK_INFO.value)
    )


# приём номера кошелька и проверка его с учётом промокода
@dp.message(StateFilter(UserStatus.EXCHANGE_SEND_PROMO))
async def check_info_promo(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()

    promo_data = await db.get_promo(msg.text)
    if not promo_data:
        sent = await msg.answer('❌ Неверный промокод')
        await sleep(3)
        await bot.delete_message(sent.chat.id, sent.message_id)
        return

    used_promo = await db.get_used_promo(promo=msg.text, user_id=msg.from_user.id)

    if (promo_data.is_onetime and used_promo) or (len(used_promo) >= promo_data.many):
        sent = await msg.answer('✅ Промокод уже применён')
        await sleep(3)
        await bot.delete_message(sent.chat.id, sent.message_id)

    else:
        promo_amount = data['total_amount'] - promo_data.rate
        if promo_amount < 1:
            promo_amount = 1

        # promo_amount = check_unique_amount(promo_amount)
        await state.update_data(data={
            'promo': promo_data.promo,
            'promo_rate': promo_data.rate,
            # 'promo_used_id': promo_data.promo_used_id,
            'total_amount': promo_amount
        })

        data = await state.get_data()
        await check_info_output(data)


# Использовать баллы
@dp.callback_query(lambda cb: cb.data.startswith(CB.USE_CASHBACK.value))
async def use_cashback(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await db.get_user_info(cb.from_user.id)

    if data['total_amount'] > user.balance:
        total_amount = data['total_amount'] - user.balance
        used_balance = user.balance
    else:
        total_amount = 1
        used_balance = (user.balance - data['total_amount']) + 1

    await db.update_user_info(user_id=cb.from_user.id, add_balance=0 - used_balance)

    # total_amount = check_unique_amount(total_amount)
    # update_balance(cb.from_user.id, return_points)

    await state.update_data(data={
        'use_points': True,
        # 'spent_points': use_points,
        'return_points': used_balance,
        'total_amount': total_amount
    })

    data = await state.get_data()
    await check_info_output(data)


# подтверждение суммы
@dp.callback_query(lambda cb: cb.data.startswith(CB.PAYMENT_ADD.value))
async def payment(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    currency = await db.get_currency(data['currency_id'])

    # total_amount = check_unique_amount(data['total_amount'])

    # await state.update_data(data={'total_amount': total_amount})
    data = await state.get_data()

    if data.get('promo'):
        promo_used_id = await db.add_used_promo(user_id=cb.from_user.id, promo=data['promo'])
    else:
        promo_used_id = 0

    order_id = await db.add_order(
        user_id=cb.from_user.id,
        coin=currency.code,
        pay_method=data['pay_method'],
        coin_sum=data['coin_sum'],
        wallet=data['wallet'],
        promo=data.get('promo'),
        promo_rate=data.get('promo_rate', 0),
        exchange_rate=data['exchange_rate'],
        percent=data['percent'],
        amount=data['amount'],
        used_points=data.get('used_point', 0),
        total_amount=data['total_amount'],
        message_id=cb.message.message_id,
        promo_used_id=promo_used_id,
        commission=data['commission'],
    )
    
    pay_method_info = await db.get_pay_method(method_id=data['pay_method_id'])
    await state.update_data(data={'order_id': order_id})

    await cb.answer(text='При переводе денег не на тот банк - возврат невозможен. '
                         'По остальным вопросам претензии принимаются в течение 24 часов.',
                    show_alert=True
                    )

    text = f'<b>Номер заявки</b> {order_id}\n' \
           f'<b>Перевод на:</b> {data["pay_method"]}\n' \
           f'<b>Номер карты:</b> <code>{pay_method_info.card}</code>\n' \
           f'<b>Сумма:</b> {data["total_amount"]} RUB\n\n' \
           f'<b>Важно:</b> Сумма должна быть точной, иначе заявка не будет выполнена и вы потеряете средства. ' \
           f'Все претензии по обмену принимаются в течении 24 часов.\n\n' \
           f'<b>ВАЖНО, ПЕРЕВОД СТРОГО НА УКАЗАННЫЙ БАНК, ИНАЧЕ ВЫ ПОТЕРЯЕТЕ СВОИ СРЕДСТВА!</b>'

    await ut.send_msg(
        msg_key=Key.PAYMENT.value,
        chat_id=cb.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_payment_conf_kb(order_id)
    )


# ожидание оплаты
@dp.callback_query(lambda cb: cb.data.startswith(CB.PAYMENT_CONF.value))
async def payment_conf(cb: CallbackQuery, state: FSMContext):
    _, order_str, action = cb.data.split(':')
    order_id = int(order_str)

    data = await state.get_data()
    await state.clear()

    if action == Action.DEL:
        await del_order(order_id, 'not_conf', cb.from_user.id, data['spent_points'], data['promo_used_id'],
                        data['chat_id'], data['message_id'], data['promo'])

    else:
        await db.update_orders(order_id=order_id, status=OrderStatus.NEW.value)

        text = f'Заявка номер {order_id}\n\n' \
               f'Статус: Обрабатывается\n' \
               f'Сумма внесения: {data["total_amount"]} RUB'

        await ut.send_msg(
            msg_key=Key.PAYMENT_CONF.value,
            chat_id=cb.chat.id,
            edit_msg=cb.message.message_id,
            text=text,
            keyboard=kb.get_payment_conf_kb(order_id)
        )

        username = f'@{cb.from_user.username}' if cb.from_user.username is not None else ''
        # text = f'<b>Новая заявка:</b>\n' \
        #        f'<b>Номер заявки:</b> {cb_data[1]}\n' \
        #        f'<b>От:</b> {cb.from_user.full_name} {username}\n' \
        #        f'<b>Валюта:</b> {data["currency_name"]}\n' \
        #        f'<b>Сумма валюты:</b> {data["sum_exchange"]}\n' \
        #        f'<b>На кошелёк:</b> {data["wallet"]}\n' \
        #        f'<b>Перевод на:</b> {data["pay_method"]}\n' \
        #        f'<b>Сумма рублей:</b> {data["total_amount"]} '

        # await cb.message.answer(text, parse_mode='html')

        text = f'<b>Новая заявка:</b>\n' \
               f'<b>Номер заявки:</b> {order_id}\n' \
               f'<b>От:</b> {cb.from_user.full_name} {username}\n' \
               f'<b>Валюта:</b> {data["currency_name"]}\n' \
               f'<b>Сумма валюты:</b> <code>{data["sum_exchange"]}</code>\n' \
               f'<b>На кошелёк:</b> <code>{data["wallet"]}</code>\n' \
               f'<b>Перевод на:</b> {data["pay_method"]}\n' \
               f'<b>Сумма рублей:</b> <code>{data["total_amount"]}</code>'
        try:
            await bot.send_message(Config.access_chat, text, parse_mode='html')
        except:
            text = f'<b>Новая заявка:</b>\n' \
                   f'<b>Номер заявки:</b> {order_id}\n' \
                   f'<b>От:</b> {cb.from_user.full_name} {username}\n' \
                   f'<b>Валюта:</b> {data["currency_name"]}\n' \
                   f'<b>Сумма валюты:</b> {data["sum_exchange"]}\n' \
                   f'<b>На кошелёк:</b> {data["wallet"]}\n' \
                   f'<b>Перевод на:</b> {data["pay_method"]}\n' \
                   f'<b>Сумма рублей:</b> {data["total_amount"]} '
            await bot.send_message(Config.access_chat, text, parse_mode='html')


