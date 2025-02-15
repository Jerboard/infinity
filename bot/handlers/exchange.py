from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter

from asyncio import sleep
from datetime import datetime, timedelta

import db
import keyboards as kb
from config import Config
from init import dp, bot
import utils as ut
from enums import CB, Key, UserStatus, Action, OrderStatus, InputType, PaymentStatus


# продать старт инлайн
@dp.callback_query(lambda cb: cb.data.startswith(CB.SELL.value))
async def russian_rub_inline(cb: CallbackQuery, state: FSMContext):
    await state.clear()

    user = await db.get_user_info(cb.from_user.id)
    if user.ban:
        await cb.message.answer(
            'Ваш аккаунт заблокирован - по вопросам можете обратиться к  @manager_Infinity'
        )

    await ut.russian_rub(cb.message, edit_msg=cb.message.message_id)


# старт обмена инлайн.  Выбор валюты
@dp.callback_query(lambda cb: cb.data.startswith(CB.EXCHANGE.value))
async def select_currency_inline(cb: CallbackQuery, state: FSMContext):
    await state.clear()

    user = await db.get_user_info(cb.from_user.id)
    if user.ban:
        await cb.message.answer(
            'Ваш аккаунт заблокирован - по вопросам можете обратиться к  @manager_Infinity'
        )

    await ut.select_currency(cb.message, state, edit_msg=cb.message.message_id)


# выбор способа оплаты
@dp.callback_query(lambda cb: cb.data.startswith(CB.SEND_SUM.value))
async def send_sum(cb: CallbackQuery, state: FSMContext):
    # _, method_id_str = cb.data.split(':')
    # method_id = int(method_id_str)

    _, currency_id_str = cb.data.split(':')
    currency_id = int(currency_id_str)

    currency = await db.get_currency(currency_id=currency_id)
    currency_name = f'{currency.name} ({currency.code})'
    await state.update_data(data={
        'user_id': cb.from_user.id,
        'currency_id': currency.id,
        'currency_name': currency_name,
        'message_id': cb.message.message_id
    })

    # await state.update_data(data={'pay_method_id': method_id})
    # data = await state.get_data()

    # currency = await db.get_currency(currency_id=data['currency_id'])

    min_sum = currency.min if currency.min != 0 else 'Без ограничения'
    msg_key = ut.get_send_sum_key(currency.code)
    msg_data = await db.get_msg(msg_key)
    text = msg_data.text.format(
        # currency_name=data['currency_name'],
        currency_name=currency_name,
        min_sum=min_sum,
        min_sum_str=str(min_sum).replace(".", ",")
    )

    await state.set_state(UserStatus.EXCHANGE_SEND_SUM)

    await ut.send_msg(
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        msg_data=msg_data,
        text=text,
        keyboard=kb.get_cancel_kb()
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

        input_type: str = InputType.RUB.value if input_sum > currency.max else InputType.COIN.value
        check_sum = input_sum if input_type == InputType.COIN else input_sum / currency.rate

        # если некорректная сумма - просит новую
        if check_sum > currency.max or check_sum < currency.min:
            min_rub = round(currency.rate * currency.min)
            max_rub = round(currency.rate * currency.max)
            text = (
                f'❌ Некорректная сумма\n'
                f'Сумма должна быть меньше:\n{currency.max} {currency.code} {max_rub} руб.\n'
                f'И больше:\n{currency.min} {currency.code} {min_rub} руб.'
            )

            msg_key = ut.get_send_sum_key(currency.code)
            sent = await ut.send_msg(
                msg_key=msg_key,
                chat_id=msg.chat.id,
                edit_msg=data['message_id'],
                text=text,
            )
            # await state.update_data(data={'message_id': sent.message_id})

        else:
            user_data = await db.get_user_info(msg.from_user.id)
            # balance = user_data.referral_points + user_data.cashback
            promo = await db.get_used_promo(user_id=msg.from_user.id, used=False)
            info = await db.get_info()

            await state.update_data(data={
                'input_sum_str': msg.text,
                'start_time': datetime.now(),
                'coin_rate': currency.rate,
                'input_sum': input_sum,
                'input_type': input_type,
                'commission': currency.commission,
                'percent': currency.ratio,
                'coin_round': currency.round,
                'buy_rate': currency.buy_price,
                'cashback_rate': info.cashback,
                'currency_code': currency.code,
                'promo_data': promo,
                'used_promo': False,
                'used_balance': False,
                'user_info': user_data,
            })

            await ut.main_exchange(state, del_msg=True)


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

    await state.update_data(data={
        'used_balance': True,
    })
    await ut.main_exchange(state)


# вернуться к
@dp.callback_query(lambda cb: cb.data.startswith(CB.BACK_CHECK_INFO.value))
async def back_check_info(cb: CallbackQuery, state: FSMContext):
    await ut.main_exchange(state)


# выбор способа оплаты
@dp.callback_query(lambda cb: cb.data.startswith(CB.SELECT_PAYMENT.value))
async def select_payment(cb: CallbackQuery, state: FSMContext):
    await ut.send_msg(
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        msg_key=Key.SELECT_PAY_METHOD.value,
        keyboard=kb.get_pay_method_kb()
        # keyboard=kb.get_pay_method_kb(pay_methods)
    )


# выбор кошелька LevL7S8DNFGQWnRrtjzhEJHRcPBMYCLwWC ltc
@dp.callback_query(lambda cb: cb.data.startswith(CB.SEND_WALLET.value))
async def send_wallet(cb: CallbackQuery, state: FSMContext):
    _, method_type = cb.data.split(':')

    data = await state.get_data()

    pay_method = await ut.get_details_api(
        request_id=1,
        amount=data['total_amount'],
        method_type=method_type
    )

    if not pay_method:
        await cb.answer('❌ Нет свободных реквизитов', show_alert=True)
        return

    await state.set_state(UserStatus.EXCHANGE_SEND_WALLET)
    await state.update_data(data={
        'request_id': pay_method['request_id'],
        'pay_method_id': pay_method['id'],
        'pay_method_name': pay_method['name'],
        'pay_method_description': pay_method['description'],
        'pay_method_details': pay_method['details'],
    })

    msg_data = await db.get_msg(Key.SEND_WALLET.value)

    text = msg_data.text.format(currency_name=data["currency_name"])
    await ut.send_msg(
        msg_data=msg_data,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_cancel_kb()
    )


# приём номера кошелька и проверка его
@dp.message(StateFilter(UserStatus.EXCHANGE_SEND_WALLET))
async def check_wallet(msg: Message, state: FSMContext):
    # await msg.delete()

    data = await state.get_data()

    if not ut.check_valid_wallet(coin=data['currency_code'], wallet=msg.text):
        await ut.send_time_message(chat_id=msg.chat.id, text='❌ Некорректный адрес кошелька', msg_ids=[msg.message_id])
        return

    await state.update_data(data={'wallet': msg.text})

    if data.get('promo_id'):
        await db.update_used_promo(promo_id=data['promo_id'], used=True)

    # списываем баллы
    if data.get('used_balance'):
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
        pay_method_id=data['pay_method_id'],
        pay_method=data['pay_method_name'],
        card=data['pay_method_details'],
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
        # message_id=data['message_id'],
        promo_used_id=data.get('promo_id', 0),
        commission=data['commission'],
        profit=data['profit'],
        cashback=data['cashback'],
        request_id=data['request_id'],
    )

    msg_data = await db.get_msg(Key.PAYMENT.value)
    text = msg_data.text.format(
        pay_method_name=data['pay_method_name'],
        pay_method_card=data['pay_method_details'],
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
    await db.update_order(order_id=order_id, message_id=sent.message_id)

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
        order = await db.get_order(order_id)
        thirty_minutes_ago = datetime.now() - timedelta(minutes=Config.order_live_time)
        # if order.created_at < thirty_minutes_ago and not Config.debug:
        if order.created_at < thirty_minutes_ago:
            await cb.message.answer('❌ Заказ устарел. Реквизиты более не действительны.')
            await ut.del_order(order)
            return

        # обновляем заказ в базе
        await db.update_order(order_id=order_id, status=OrderStatus.NEW.value)
        order = await db.get_order(order_id)

        # обновляем на сервисе
        await ut.close_detail_api(
            request_id=order.request_id,
            amount=order.total_amount,
            status=PaymentStatus.WAITING.value
        )

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

        username = f'@{cb.from_user.username}' if cb.from_user.username is not None else ''
        text = f'<b>Новая заявка:</b>\n' \
               f'<b>Номер заявки:</b> {order_id}\n' \
               f'<b>От:</b> {cb.from_user.full_name} {username}\n' \
               f'<b>Валюта:</b> {order.coin}\n' \
               f'<b>Сумма валюты:</b> <code>{order.coin_sum}</code>\n' \
               f'<b>На кошелёк:</b> <code>{order.wallet}</code>\n' \
               f'<b>Перевод на:</b> {order.pay_method}\n' \
               f'<b>Сумма рублей:</b> <code>{order.total_amount}</code>'

        await bot.send_message(Config.operator_chat, text)

        ut.add_order_row(order=order, row=order.row)

