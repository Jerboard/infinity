from aiogram.types import Message, InlineKeyboardMarkup, InputMediaPhoto, FSInputFile
from random import choice

import db
import keyboards as kb
from init import bot
from config import Config
from data import capcha_list


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



# отправляет сообщение
async def send_msg(msg_key: str, chat_id: int,  edit_msg: int = None, kb: InlineKeyboardMarkup = None) -> Message:
    # если тест, чтоб возвращал тестовую картинку
    if Config.debug:
        msg_key = 'test'

    msg_data = await db.get_msg(msg_key)

    # если фото обновлено и не имеет своего ключа
    if Config.debug:
        photo_id = 'test'
        update = False
    elif msg_data.photo_id:
        photo_id = msg_data.photo_id
        update = False
    else:
        photo_id = FSInputFile(msg_data.photo_path)
        update = True

    if edit_msg:
        photo = InputMediaPhoto(media=photo_id, caption=msg_data.text)
        sent = await bot.edit_message_media(
            chat_id=chat_id,
            message_id=edit_msg,
            media=photo,
            reply_markup=kb
        )

    else:
        sent = await bot.send_photo(
            chat_id=chat_id,
            photo=photo_id,
            caption=msg_data.text,
            reply_markup=kb
        )

    if update:
        await db.update_msg(msg_data.id, photo_id=sent.photo[-1].file_id)

    return sent
