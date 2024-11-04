from aiogram.types import Message, InlineKeyboardMarkup, InputMediaPhoto, FSInputFile, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType
from asyncio import sleep
from random import choice, sample

import typing as t

import db
import keyboards as kb
from init import bot
from config import Config
from data import capcha_list
import utils as ut
from enums import Key, UserStatus, OrderStatus


# отправляет сообщение
async def send_capcha(chat_id: int, first_name: str, referrer: str = None) -> None:
    # selected_capcha = [choice(capcha_list) for _ in range(6)]
    selected_capcha = sample(capcha_list, 6)  # выбираем 6 уникальных фруктов
    match_char = choice(selected_capcha)
    text = f'Привет {first_name}\n\nВыбери <b>{match_char[0]}</b>'
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=kb.get_capcha_kb(items=selected_capcha, match=match_char, referrer=referrer)
    )


# временное сообщение
async def send_time_message(chat_id: int, text: str) -> None:
    sent = await bot.send_message(chat_id=chat_id, text=text)
    await sleep(3)
    await sent.delete()


# обрабатывает текст. заменяет неподдерживаемые теги
def parse_text(text: str) -> str:
    return text.replace('<br>', '\n')


# отправляет сообщение
async def send_msg(
        chat_id: int,
        msg_key: str = None,
        msg_data: db.MsgRow = None,
        text: str = None,
        edit_msg: int = None,
        keyboard: t.Union[InlineKeyboardMarkup, ReplyKeyboardMarkup] = None
) -> Message:
    if not msg_data:
        msg_data = await db.get_msg(msg_key)

    if msg_data.photo_id and msg_data.bot_id == Config.bot_id:
        photo_id = msg_data.photo_id
        update = False
    else:
        photo_id = FSInputFile(msg_data.photo_path)
        update = True

    # print(text)
    text = parse_text(text) if text else parse_text(msg_data.text)

    if edit_msg:
        photo = InputMediaPhoto(media=photo_id, caption=text)
        sent = await bot.edit_message_media(
            chat_id=chat_id,
            message_id=edit_msg,
            media=photo,
            reply_markup=keyboard
        )

    else:
        sent = await bot.send_photo(
            chat_id=chat_id,
            photo=photo_id,
            caption=text,
            reply_markup=keyboard
        )

    if update:
        await db.update_msg(msg_data.id, photo_id=sent.photo[-1].file_id, bot_id=Config.bot_id)

    return sent


async def main_exchange(state: FSMContext, del_msg: bool = False):
    data = await state.get_data()

    ex_data = ut.amount_calculator(
        coin_rate=data.get('coin_rate'),
        user_rub_sum=data.get('user_rub_sum'),
        commission=data.get('commission'),
        infinity_percent=data.get('percent'),
        coin_round=data.get('coin_round'),
        buy_rate=data.get('buy_rate'),
        cashback_rate=data.get('cashback_rate'),
        promo_rate=data.get('promo_rate'),
        used_balance=data.get('used_balance'),
        user_info=data.get('user_info')
    )

    await state.update_data(**ex_data)
    data = await state.get_data()

    pay_methods = await db.get_all_pay_method()

    msg_data = await db.get_msg(Key.EXCHANGE.value)
    text = msg_data.text.format(
        currency_rate=data['coin_rate'],
        # sum_coin=data['coin_sum'],
        sum_coin=data['input_sum'] if data.get('input_coin') else data['coin_sum'],
        currency_code=data['currency_code'],
        sum_rub=data['user_rub_sum'],
        balance=f'<s>{data["balance"]}</s>' if data.get('used_balance') else data['balance'],
        pay_string=data['pay_string']
    )

    # print(f'text:\n{text}')
    if del_msg:
        await bot.delete_message(chat_id=data['user_id'], message_id=data['message_id'])
        edit_msg = None
    else:
        edit_msg = data['message_id']

    # promo = await db.get_used_promo(user_id=data['user_id'])  # if not data.get('used_promo') else None
    promo: db.UsedPromoRow = data['promo_data']

    sent = await ut.send_msg(
        msg_data=msg_data,
        chat_id=data['user_id'],
        edit_msg=edit_msg,
        text=text,
        keyboard=kb.get_main_exchange_kb(
            pay_methods=pay_methods,
            total_amount=data['total_amount'],
            promo=promo
        )
    )
    await state.update_data(data={'message_id': sent.message_id})


# отправляет сообщение всех типов
async def send_any_message(msg: Message, chat_id: int, keyboard: InlineKeyboardMarkup = None) -> Message:
    if msg.content_type == ContentType.TEXT:
        sent = await bot.send_message(
            chat_id=chat_id,
            text=msg.text,
            entities=msg.entities,
            parse_mode=None,
            reply_markup=keyboard
        )

    elif msg.content_type == ContentType.PHOTO:
        sent = await bot.send_photo (
            chat_id=chat_id,
            photo=msg.photo[-1].file_id,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
            parse_mode=None,
            reply_markup=keyboard
        )

    elif msg.content_type == ContentType.VIDEO:
        sent = await bot.send_video (
            chat_id=chat_id,
            video=msg.video.file_id,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
            parse_mode=None,
            reply_markup=keyboard
        )

    elif msg.content_type == ContentType.VIDEO_NOTE:
        sent = await bot.send_video_note (
            chat_id=chat_id,
            video_note=msg.video_note.file_id,
            reply_markup=keyboard
        )

    elif msg.content_type == ContentType.ANIMATION:
        sent = await bot.send_animation (
            chat_id=chat_id,
            animation=msg.animation.file_id,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
            parse_mode=None,
            reply_markup=keyboard
        )

    elif msg.content_type == ContentType.VOICE:
        sent = await bot.send_voice (
            chat_id=chat_id,
            voice=msg.voice.file_id,
            reply_markup=keyboard
        )

    elif msg.content_type == ContentType.DOCUMENT:
        sent = await bot.send_document (
            chat_id=chat_id,
            voice=msg.document.file_id,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
            parse_mode=None,
            reply_markup=keyboard
        )

    else:
        sent = None

    return sent


# кнопка продать
async def russian_rub(msg: Message, edit_msg: int = None):
    await ut.send_msg(
        msg_key=Key.SELL.value,
        chat_id=msg.chat.id,
        edit_msg=edit_msg,
        keyboard=kb.get_sell_kb()
    )


# старт обмена
async def select_currency(msg: Message, state: FSMContext, edit_msg: int = None):
    await state.clear()
    check_orders = await db.get_orders(user_id=msg.from_user.id, check=True)

    if check_orders:
        text = 'У вас ещё осталась незакрытая заявка'
        await ut.send_time_message(chat_id=msg.chat.id, text=text)
    else:
        await state.set_state(UserStatus.EXCHANGE)

        currency = await db.get_all_currency()
        await ut.send_msg(
            msg_key=Key.SELECT_CURRENCY.value,
            chat_id=msg.chat.id,
            edit_msg=edit_msg,
            keyboard=kb.get_currency_list_kb(currency)
        )


async def start_acc_send(msg: Message, from_user_id: int = None):
    user_id = from_user_id or msg.from_user.id

    user = await db.get_user_info(user_id)
    referrers = await db.get_users(referrer=user_id)
    exchanges = await db.get_orders(user_id=user_id, status=OrderStatus.SUC.value)
    active_promo = await db.get_used_promo(user_id=user_id, used=False)
    # old_promo = await db.get_used_promo(user_id=msg.from_user.id)

    if user.custom_referral_lvl_id:
        lvl = user.custom_referral_lvl_id

    else:
        ref_lvl = await db.get_referral_lvl(count_user=len(referrers))
        lvl = ref_lvl.id or 1

    msg_data = await db.get_msg(Key.ACCOUNT.value)
    text = msg_data.text.format(
        user_id=user_id,
        count_ex=len(exchanges),
        sum_exchange=sum(exchange.total_amount for exchange in exchanges),
        count_ref=len(referrers),
        ref_lvl=lvl,
        balance=user.referral_points + user.cashback,
        ref_link=f'{Config.bot_link}?start={user.ref_code}'
    )

    if active_promo:
        text += f'\n\nАктивирован промокод: {active_promo.promo} на {active_promo.rate}%'

    await ut.send_msg(
        msg_data=msg_data,
        chat_id=msg.chat.id,
        # edit_msg=msg.message_id,
        text=text,
        keyboard=kb.get_account_kb()
    )


async def antispam_sent(msg: Message, edit_msg: int = None):
    await ut.send_msg(
        msg_key=Key.ANTISPAM.value,
        chat_id=msg.chat.id,
        edit_msg=edit_msg,
        keyboard=kb.get_antispam_user_kb()
    )


# Раздел "О нас"
async def info_send(msg: Message, edit_msg: int = None):
    await ut.send_msg(
        msg_key=Key.INFO.value,
        chat_id=msg.chat.id,
        edit_msg=edit_msg,
        keyboard=kb.get_info_kb()
    )



