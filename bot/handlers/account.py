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
from enums import CB, Key, UserStatus, Action, OrderStatus, Coin


# Аккаунт старт
@dp.callback_query(lambda cb: cb.data.startswith(CB.ACCOUNT.value))
async def start_account(cb: CallbackQuery, state: FSMContext):
    await state.clear()

    user = await db.get_user_info(cb.from_user.id)
    referrers = await db.get_users(referrer=cb.from_user.id)
    count_ref = len(referrers)
    exchanges = await db.get_orders(user_id=cb.from_user.id, status=OrderStatus.SUC.value)
    count_ex = len(exchanges)
    sum_exchange = sum(exchange.total_amount for exchange in exchanges)
    ref_lvl = user.custom_referral_lvl_id
    balance = user.balance

    text = (
        f'ID пользователя: {cb.from_user.id}\n'
        f'Кол-во обменов: {count_ex} ({sum_exchange} Руб)\n'
        f'Приглашено пользователей: {count_ref}\n'
        f'Уровень реферальной программы: {ref_lvl}\n'
        f'Доступный баланс:  {balance} руб\n\n'
        f'Реф ссылка: <code>{Config.bot_link}?start={cb.from_user.id}</code>'
    )

    await ut.send_msg(
        msg_key=Key.ACCOUNT.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_account_kb()
    )


# Промокод
@dp.callback_query(lambda cb: cb.data.startswith(CB.PROMO.value))
async def promo(cb: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatus.ACC_PROMO)
    await state.update_data(data={'message_id': cb.message.message_id})
    text = (
        'Использование промокода позволяет вам получить скидку при обмене.\n'
        'Он будет автоматически применен при создании заявки.\n'
        'Скидка зависит от % вашего промо и прибыли сервиса.\n\n'
        'Введите ваш промокод'
    )
    await ut.send_msg(
        msg_key=Key.PROMO.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
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

        old_promo = await db.get_used_promo(user_id=msg.from_user.id)

        if old_promo:
            print(f'old_promo: {old_promo}')
            # old_promo_info = await db.get_promo(promo_id=old_promo.id)
            await state.update_data(data={
                'old_promo_id': old_promo.id,
                'new_promo_rate': promo_data.rate,
                'new_promo': promo_data.promo,
            })

            text = (
                f'У вас уже активирован промокод {old_promo.promo} на скидку в {old_promo.rate}%\n'
                f'Вы уверены, что хотите заменить его?\n'
                f'Важно: при активации нового промокода - старый сгорает!'
            )
            await ut.send_msg(
                msg_key=Key.REPLACE_PROMO.value,
                chat_id=msg.chat.id,
                edit_msg=data['message_id'],
                text=text,
                keyboard=kb.get_replace_promo_kb()
            )

        else:
            await db.add_used_promo(promo=promo_data.promo, user_id=msg.from_user.id, rate=promo_data.rate)

            text = (f'Ваш промокод <b>{promo_data.promo}</b> успешно применен. Скидка составляет {promo_data.rate}% \n'
                    f'Удачных обменов!')
            await state.clear()
            await ut.send_msg(
                msg_key=Key.REPLACE_PROMO.value,
                chat_id=msg.chat.id,
                edit_msg=data['message_id'],
                text=text,
                keyboard=kb.get_back_kb(CB.ACCOUNT.value)
            )

    else:
        sent = await msg.answer('Промо не найден')
        await sleep(3)
        await sent.delete()


# Промокод меняем на новый
@dp.callback_query(lambda cb: cb.data.startswith(CB.REPLACE_PROMO.value))
async def replace_promo(cb: CallbackQuery, state: FSMContext):
    # _, old_promo, new_promo = cb.data.split(':')
    # old_promo_id = int(old_promo)
    # new_promo_id = int(new_promo)

    data = await state.get_data()
    print(f'data: {data}')
    await state.clear()

    await db.update_used_promo(user_id=cb.from_user.id, used=True)
    await db.add_used_promo(promo=data['new_promo'], user_id=cb.from_user.id, rate=data['new_promo_rate'])

    # promo_data = await db.get_promo(promo_id=new_promo_id)
    text = (f'Ваш промокод {data["new_promo"]} успешно применен. Скидка составляет {data["new_promo_rate"]}% \n'
            f'Удачных обменов!')

    await ut.send_msg(
        msg_key=Key.REPLACE_PROMO.value,
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
    count_ref = len(referrers)
    exchanges = await db.get_orders(referrer_id=cb.from_user.id, status=OrderStatus.SUC.value)
    sum_ref_exchange = round(sum(exchange.total_amount for exchange in exchanges) * 0.03)
    ref_lvl = user.custom_referral_lvl_id
    cashback = user.cashback

    text = (
        f'Зарабатывай вместе с The Infinity Exchange\n'
        f'Наша партнерская программа поможет тебе в этом.\n\n'
        f'Для того, чтобы пригласить других пользователей '
        f'отправь им свою ссылку, которая указана ниже:\n\n'
        f'<code>{Config.bot_link}?start={cb.from_user.id}</code> \n\n'
        f'Чем больше приглашенных людей, тем выше твой реферальный процент!\n\n'
        f'от 1 до 20 приглашенных - уровень 1 (10% от прибыли со сделки)\n'
        f'от 20 до 40 пользователей - уровень 2 (15% от прибыли со сделки)\n'
        f'от 40 до 80 пользователей - уровень 3 (20% от прибыли со сделки)\n'
        f'от 80 и выше - уровень 4 (25% от прибыли со сделки)\n\n'
        f'Ваш уровень реферальной программы: {ref_lvl}\n'
        f'Приглашено пользователей: {count_ref}\n'
        f'Всего заработано с партнерами: {sum_ref_exchange} Руб.\n'
        f'Доступный баланс: {cashback} Руб.\n\n'
        f'Также, имеются индивидуальные условия для владельцев магазина и других источников трафика - '
        f'уточняйте у менеджера\n'
        f'(@manager_Infinity)'
    )

    await ut.send_msg(
        msg_key=Key.PARTNER.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_back_kb(CB.ACCOUNT.value)
    )


# Кнопка партнёрская программа
@dp.callback_query(lambda cb: cb.data.startswith(CB.CASHBACK.value))
async def partner(cb: CallbackQuery, state: FSMContext):
    user = await db.get_user_info(cb.from_user.id)
    referrers = await db.get_orders(referrer_id=cb.from_user.id, status=OrderStatus.SUC.value)
    ref_order_count = len(referrers)
    cashback = user.cashback

    text = (
        f'При каждом совершенном обмене, вам будет начислено 3% от прибыли сервиса с обмена. \n\n'
        f'Баланс кэшбека автоматически начисляется в "доступный баланс" - '
        f'вы можете потратить эти бонусы как для скидки при обмене, так и вывести их себе на '
        f'BTC кошелек по кнопке "вывод бонусов"\n\n'
        f'• всего получено кэшбека: {cashback} RUB\n'
        f'• совершено обменов: {ref_order_count}\n'
    )

    await ut.send_msg(
        msg_key=Key.CASHBACK.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_back_kb(CB.ACCOUNT.value)
    )


# Кнопка партнёрская вывода
@dp.callback_query(lambda cb: cb.data.startswith(CB.TAKE_BONUS.value))
async def partner(cb: CallbackQuery, state: FSMContext):
    user = await db.get_user_info(cb.from_user.id)
    balance = user.cashback + user.referral_points

    await state.set_state(UserStatus.TAKE_CASHBACK)
    await state.update_data(data={'balance': balance, 'cashback': user.cashback, 'points': user.referral_points})

    text = (
        f'Минимальная сумма вывода - 1000 RUB\n'
        f'Ваш баланс: {balance} RUB\n'
        f'• выплата проводится на BTC кошелек\n'
        f'• оформить вывод, можно в любой день недели!\n\n'
        f'Укажите ваш BTC кошелек'
    )

    await ut.send_msg(
        msg_key=Key.TAKE_BONUS.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_back_kb(CB.ACCOUNT.value)
    )


# приём кошелька
@dp.message(StateFilter(UserStatus.TAKE_CASHBACK))
async def take_cashback_step_2(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    if data['balance'] < 1000:
        sent = await msg.answer('❌Ваш баланс меньше 1000р.')
        await sleep(3)
        await sent.delete()
        return

    checked_wallet = await db.get_wallet(code=Coin.BTC.value, wallet=msg.text)
    if not checked_wallet:
        checked_wallet = await ut.check_wallet(coin_code=Coin.BTC.value, wallet=msg.text)

    if not checked_wallet:
        sent = await msg.answer('❌ Некорректный адрес кошелька')
        await sleep(3)
        await sent.delete()
        return

    await state.update_data(data={'wallet': msg.text})
    text = (
        f'Вывод средств: {data["balance"]} руб.\n'
        f'На реквизиты:\n\n'
        f'{msg.text}\n\n'
        f'Если всё верно нажмите "Подтвердить" или просто отправьте новые реквизиты'
    )

    await ut.send_msg(
        msg_key=Key.TAKE_BONUS_CONF.value,
        chat_id=msg.chat.id,
        edit_msg=msg.message_id,
        text=text,
        keyboard=kb.get_back_kb(CB.TAKE_BONUS.value)
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

    text = (
        f'Заявка номер {cashback_id}\n\n'
        f'Статус: Обрабатывается\n'
        f'Сумма кешбека: {data["balance"]} RUB'
    )

    await ut.send_msg(
        msg_key=Key.TAKE_BONUS_END.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        text=text,
        keyboard=kb.get_back_kb(CB.ACCOUNT.value)
    )

    text = f'<b>Заявка на вывод кешбека:</b>\n' \
           f'<b>От:</b> {cb.from_user.full_name}\n' \
           f'<b>Сумма:</b> {data["balance"]} руб.\n' \
           f'<b>Кошелёк:</b> {data["wallet"]}'

    await bot.send_message(Config.access_chat, text)


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
        end_index = start_index + 3
        text = 'История обменов:\n'
        for order in orders[start_index:end_index]:
            text += (
                f'№{order.id} \n'
                f'Дата обмена: 16.08.24\n'
                f'Получено {order.coin_sum} {order.coin}\n'
                f'Оплачено {order.total_amount} Руб\n'
                f'Хэш транзакции: {order.hash}\n'
                f'Кэшбек: {order.cashback} Руб\n\n'
            )
        await ut.send_msg(
            msg_key=Key.HISTORY.value,
            chat_id=cb.message.chat.id,
            edit_msg=cb.message.message_id,
            text=text,
            keyboard=kb.get_history_kb(start=start_index, end_page=len(orders) >= end_index)
        )



