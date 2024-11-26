from aiogram.types import Message, InlineKeyboardMarkup, InputMediaPhoto, FSInputFile, ReplyKeyboardMarkup
from aiogram.enums.content_type import ContentType

import typing as t

import db
from init import bot
from config import Config


# отправляет сообщение
async def send_msg(
        chat_id: int,
        msg_key: str = None,
        keyboard: t.Union[InlineKeyboardMarkup, ReplyKeyboardMarkup] = None
) -> Message:
    msg_data = await db.get_msg(msg_key)

    if msg_data.photo_id and msg_data.bot_id == Config.bot_id:
        photo_id = msg_data.photo_id
        update = False
    else:
        photo_id = FSInputFile(msg_data.photo_path)
        update = True

    # text = text if text else msg_data.text

    # if edit_msg:
    #     photo = InputMediaPhoto(media=photo_id, caption=text)
    #     sent = await bot.edit_message_media(
    #         chat_id=chat_id,
    #         message_id=edit_msg,
    #         media=photo,
    #         reply_markup=keyboard
    #     )

    # else:
    sent = await bot.send_photo(
        chat_id=chat_id,
        photo=photo_id,
        caption=msg_data.text,
        reply_markup=keyboard
    )

    if update:
        await db.update_msg(msg_data.id, photo_id=sent.photo[-1].file_id, bot_id=Config.bot_id)

    return sent


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
