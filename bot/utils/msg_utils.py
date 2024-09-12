from aiogram.types import Message, InlineKeyboardMarkup, InputMediaPhoto, FSInputFile
from aiogram.fsm.context import FSMContext
from random import choice

import db
import keyboards as kb
from init import bot
from config import Config
from data import capcha_list
import utils as ut
from enums import Key


# отправляет сообщение
async def send_capcha(chat_id: int, first_name: str, referrer: str = None) -> None:
    selected_capcha = [choice(capcha_list) for _ in range(6)]
    match_char = choice(selected_capcha)
    text = f'Привет {first_name}\n\nВыбери <b>{match_char[0]}</b>'
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=kb.get_capcha_kb(items=selected_capcha, match=match_char, referrer=referrer)
    )


# обрабатывает текст. заменяет неподдерживаемые теги
def parse_text(text: str) -> str:
    return text.replace('<p>', '\n').replace('</p>', '\n').replace('<br>', '\n')
    # return text


# отправляет сообщение
async def send_msg(
        msg_key: str,
        chat_id: int,
        text: str = None,
        edit_msg: int = None,
        keyboard: InlineKeyboardMarkup = None
) -> Message:
    # если тест, чтоб возвращал тестовую картинку
    if Config.debug:
        # msg_key = Config.test_photo
        msg_key = 'test'

    msg_data = await db.get_msg(msg_key)

    # если фото обновлено и не имеет своего ключа
    if Config.debug:
        photo_id = Config.test_photo
        update = False
    elif msg_data.photo_id:
        photo_id = msg_data.photo_id
        update = False
    else:
        photo_id = FSInputFile(msg_data.photo_path)
        update = True

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
        await db.update_msg(msg_data.id, photo_id=sent.photo[-1].file_id)

    return sent


# считает сумму
async def check_info_output(state: FSMContext, del_msg: bool = False):
    data = await state.get_data()
    currency = await db.get_currency(data['currency_id'])

    text = ut.get_check_info_text(data=data, currency=currency)
    if del_msg:
        await bot.delete_message(chat_id=data['user_id'], message_id=data['message_id'])
        sent = await ut.send_msg(
            msg_key=Key.CHECK_WALLET.value,
            chat_id=data['user_id'],
            text=text,
            keyboard=kb.get_check_info_kb(use_points=data['used_points'], points=data['points'], promo=data.get('promo'))
        )
        await state.update_data(data={'message_id': sent.message_id})
    else:
        await ut.send_msg(
            msg_key=Key.CHECK_WALLET.value,
            chat_id=data['user_id'],
            edit_msg=data['message_id'],
            text=text,
            keyboard=kb.get_check_info_kb(use_points=data['used_points'], points=data['points'], promo=data.get('promo'))
        )
