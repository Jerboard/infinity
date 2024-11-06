from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from datetime import datetime

from asyncio import sleep
from datetime import datetime

import db
import keyboards as kb
from config import Config
from init import dp, bot
import utils as ut
from enums import CB, Key, UserStatus, Action, OrderStatus, Coin, MainButton


# Аккаунт старт
@dp.callback_query(lambda cb: cb.data.startswith(CB.ACCOUNT.value))
async def start_account(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await ut.start_acc_send(cb.message, from_user_id=cb.from_user.id)


# Промокод
@dp.callback_query(lambda cb: cb.data.startswith(CB.PROMO.value))
async def promo(cb: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatus.ACC_PROMO)
    await state.update_data(data={'message_id': cb.message.message_id})
    await ut.send_msg(
        msg_key=Key.PROMO.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        keyboard=kb.get_back_kb(CB.ACCOUNT.value)
    )


# приём промо
@dp.message(StateFilter(UserStatus.ACC_PROMO))
async def acc_promo(msg: Message, state: FSMContext):
    data = await state.get_data()
    await msg.delete()

    promo_data = await db.get_promo(promo=msg.text)
    if promo_data:
        used_promo = await db.get_used_promo(promo=msg.text, user_id=msg.from_user.id)
        if used_promo:
            await ut.send_time_message(chat_id=msg.chat.id, text='❗️ Вы уже использовали этот промокод')
            return

        old_promo = await db.get_used_promo(user_id=msg.from_user.id, used=False)

        if old_promo:
            # old_promo_info = await db.get_promo(promo_id=old_promo.id)
            await state.update_data(data={
                'old_promo_id': old_promo.id,
                'new_promo_rate': promo_data.rate,
                'new_promo': promo_data.promo,
            })

            msg_data = await db.get_msg(Key.REPLACE_PROMO_CONF.value)
            text = msg_data.text.format(
                active_promo=old_promo.promo,
                rate=old_promo.rate
            )
            await ut.send_msg(
                msg_data=msg_data,
                chat_id=msg.chat.id,
                edit_msg=data['message_id'],
                text=text,
                keyboard=kb.get_replace_promo_kb()
            )
        else:
            await db.add_used_promo(promo=promo_data.promo, user_id=msg.from_user.id, rate=promo_data.rate)

            msg_data = await db.get_msg(Key.REPLACE_PROMO.value)
            text = msg_data.text.format(
                promocode=promo_data.promo,
                rate=promo_data.rate
            )
            await state.clear()
            await ut.send_msg(
                msg_data=msg_data,
                chat_id=msg.chat.id,
                edit_msg=data['message_id'],
                text=text,
                keyboard=kb.get_back_kb(CB.ACCOUNT.value)
            )

    else:
        await ut.send_time_message(chat_id=msg.chat.id, text='Промо не найден')


# Промокод меняем на новый
@dp.callback_query(lambda cb: cb.data.startswith(CB.REPLACE_PROMO.value))
async def replace_promo(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    await db.update_used_promo(user_id=cb.from_user.id, used=True)
    await db.add_used_promo(promo=data['new_promo'], user_id=cb.from_user.id, rate=data['new_promo_rate'])

    msg_data = await db.get_msg(Key.REPLACE_PROMO.value)
    text = msg_data.text.format(
        promocode=data["new_promo"],
        rate=data["new_promo_rate"]
    )

    await ut.send_msg(
        msg_data=msg_data,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_back_kb(CB.ACCOUNT.value)
    )


# Кнопка партнёрская программа
@dp.callback_query(lambda cb: cb.data.startswith(CB.PARTNER.value))
async def partner(cb: CallbackQuery, state: FSMContext):
    user = await db.get_user_info(cb.from_user.id)
    referrers = await db.get_users(referrer=cb.from_user.id)
    exchanges = await db.get_orders(referrer_id=cb.from_user.id, status=OrderStatus.SUC.value)

    # проверяем реф уровень
    ref_lvl = user.custom_referral_lvl_id
    if not ref_lvl:
        lvl = await db.get_referral_lvl(count_user=len(referrers))
        ref_lvl = lvl.id

    msg_data = await db.get_msg(Key.PARTNER.value)
    text = msg_data.text.format(
        sum_ref_exchange=round(sum(exchange.profit for exchange in exchanges) * 0.01),
        count_ref=len(referrers),
        ref_lvl=ref_lvl,
        cashback=user.referral_points,
        ref_link=f'{Config.bot_link}?start={user.ref_code}'
    )

    await ut.send_msg(
        msg_data=msg_data,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_back_kb(CB.ACCOUNT.value)
    )


# Кнопка кешбек
@dp.callback_query(lambda cb: cb.data.startswith(CB.CASHBACK.value))
async def cashback(cb: CallbackQuery, state: FSMContext):
    user = await db.get_user_info(cb.from_user.id)
    referrers = await db.get_orders(user_id=cb.from_user.id, status=OrderStatus.SUC.value)

    msg_data = await db.get_msg(Key.CASHBACK.value)
    text = msg_data.text.format(
        ref_order_count=len(referrers),
        cashback=user.cashback
    )

    await ut.send_msg(
        msg_data=msg_data,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_back_kb(CB.ACCOUNT.value)
    )


# Кнопка партнёрская вывода
@dp.callback_query(lambda cb: cb.data.startswith(CB.TAKE_BONUS.value))
async def take_bonus(cb: CallbackQuery, state: FSMContext):
    user = await db.get_user_info(cb.from_user.id)
    balance = user.cashback + user.referral_points

    await state.set_state(UserStatus.TAKE_CASHBACK)

    msg_data = await db.get_msg(Key.TAKE_BONUS.value)
    text = msg_data.text.format(
        balance=balance
    )

    sent = await ut.send_msg(
        msg_data=msg_data,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_back_kb(CB.ACCOUNT.value)
    )
    await state.update_data(data={
        'balance': balance,
        'cashback': user.cashback,
        'points': user.referral_points,
        'message_id': sent.message_id,
    })


# приём кошелька
@dp.message(StateFilter(UserStatus.TAKE_CASHBACK))
async def take_cashback_step_2(msg: Message, state: FSMContext):
    # await msg.delete()
    data = await state.get_data()
    if data['balance'] < 1000:
        sent = await msg.answer('❌Ваш баланс меньше 1000р.')
        await sleep(3)
        await sent.delete()
        return

    # checked_wallet = await db.get_wallet(code=Coin.BTC.value, wallet=msg.text)
    # if not checked_wallet:
    #     checked_wallet = await ut.check_wallet(coin_code=Coin.BTC.value, wallet=msg.text)

    # if not checked_wallet:
    if not ut.check_valid_wallet(coin=Coin.BTC.value, wallet=msg.text):
        sent = await msg.answer('❌ Некорректный адрес кошелька')
        await sleep(3)
        await sent.delete()
        return

    await state.update_data(data={'wallet': msg.text})

    msg_data = await db.get_msg(Key.TAKE_BONUS_CONF.value)
    text = msg_data.text.format(
        balance=data["balance"],
        wallet=msg.text
    )

    await bot.delete_message(chat_id=msg.chat.id, message_id=data['message_id'])
    await ut.send_msg(
        msg_data=msg_data,
        chat_id=msg.chat.id,
        # edit_msg=msg.message_id,
        text=text,
        keyboard=kb.get_conf_take_bonus_kb()
    )


# вывод кешбека
@dp.callback_query(lambda cb: cb.data.startswith(CB.TAKE_BONUS_CONF.value))
async def take_bonus_end(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    await db.update_user_info(
        user_id=cb.from_user.id,
        add_point=0 - data['points'],
        add_cashback=0 - data['cashback'],
    )

    cashback_id = await db.add_cb_order(
        user_id=cb.from_user.id,
        coin=Coin.BTC.value,
        wallet=data['wallet'],
        balance=data['balance'],
        points=data['points'],
        cashback=data['cashback'],
        message_id=cb.from_user.id
    )

    msg_data = await db.get_msg(Key.TAKE_BONUS_END.value)
    text = msg_data.text.format(
        balance=data["cashback"],
        cashback_id=cashback_id
    )

    await ut.send_msg(
        msg_data=msg_data,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_back_kb(CB.ACCOUNT.value)
    )

    text = f'<b>Заявка на вывод кешбека:</b>\n' \
           f'<b>От:</b> {cb.from_user.full_name}\n' \
           f'<b>Сумма:</b> {data["cashback"]} руб.\n' \
           f'<b>Кошелёк:</b> {data["wallet"]}'

    await bot.send_message(Config.access_chat, text)

    # добавляем в таблицу
    order_cb = await db.get_cb_order(cashback_id)
    row = ut.add_cd_order_row(order_cb)
    await db.update_cb_orders(order_id=cashback_id, row=row)


# история обменов
@dp.callback_query(lambda cb: cb.data.startswith(CB.HISTORY.value))
async def take_bonus_end(cb: CallbackQuery, state: FSMContext):
    _, start = cb.data.split(':')
    start_index = int(start)

    orders = await db.get_orders(user_id=cb.from_user.id, status=OrderStatus.SUC.value, desc_order=True)
    if len(orders) == 0:
        text = '❗️ Вы не совершили ни одного обмена'
        await ut.send_msg(
            msg_key=Key.HISTORY.value,
            chat_id=cb.message.chat.id,
            edit_msg=cb.message.message_id,
            text=text,
            keyboard=kb.get_back_kb(CB.ACCOUNT.value)
        )
    else:
        msg_data = await db.get_msg(Key.HISTORY.value)

        end_index = start_index + 3
        text = 'История обменов:\n'
        for order in orders[start_index:end_index]:
            text += msg_data.text.format(
                order_id=order.id,
                date=order.created_at.date().strftime('%d.%m.%y'),
                coin_sum=order.coin_sum,
                coin=order.coin,
                total_amount=order.total_amount,
                order_hash=order.hash,
                cashback=order.cashback or '0'
            )
            text += '\n\n'

        await ut.send_msg(
            msg_data=msg_data,
            chat_id=cb.message.chat.id,
            edit_msg=cb.message.message_id,
            text=text,
            keyboard=kb.get_history_kb(start=start_index, end_page=len(orders) > end_index)
        )



