from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.enums.content_type import ContentType
from datetime import datetime

import db
import keyboards as kb
from config import Config
from init import dp, bot, log_error
from enums import CB, Action


# филтр админов
def admin_filter(user_id: int):
    if Config.debug:
        admins = [524275902, 1879617805, 2028268703]
    else:
        admins = [1879617805, 2028268703]
    return user_id in admins


# приём сообщения
@dp.message(lambda msg: admin_filter(msg.from_user.id))
async def sending_1(msg: Message):
    await msg.delete()

    if msg.content_type == ContentType.TEXT:
        await msg.answer(text=msg.text, entities=msg.entities, reply_markup=kb.get_sending_kb())

    elif msg.content_type == ContentType.PHOTO:
        await msg.answer_photo(
            photo=msg.photo[-1].file_id,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
            reply_markup=kb.get_sending_kb())

    elif msg.content_type == ContentType.VIDEO:
        await msg.answer_video(
            video=msg.video.file_id,
            caption=msg.caption,
            caption_entities=msg.caption_entities,
            reply_markup=kb.get_sending_kb()
        )


# рассылает или удаляет сообщение
@dp.callback_query(lambda cb: cb.data.startswith(CB.SENDING_MESSAGE.value))
async def sending_message(cb: CallbackQuery):
    _, action = cb.data.split(':')
    if action == Action.DEL:
        await cb.message.delete()

    else:
        sent = await cb.message.answer('⏳')
        users = await db.get_users()
        sending = len(users)
        for user in users:
            try:
                if cb.message.content_type == ContentType.TEXT:
                    await bot.send_message(
                        chat_id=user.user_id,
                        text=cb.message.text,
                        entities=cb.message.entities,
                        reply_markup=ReplyKeyboardRemove()
                    )

                elif cb.message.content_type == ContentType.PHOTO:
                    await bot.send_photo(
                        chat_id=user.user_id,
                        photo=cb.message.photo[-1].file_id,
                        caption=cb.message.caption,
                        caption_entities=cb.message.caption_entities,
                        reply_markup=ReplyKeyboardRemove()
                    )

                elif cb.message.content_type == ContentType:
                    await bot.send_video(
                        chat_id=user.user_id,
                        video=cb.message.animation.file_id,
                        caption=cb.message.caption,
                        caption_entities=cb.message.caption_entities,
                        reply_markup=ReplyKeyboardRemove()
                    )

            except Exception as ex:
                sending -= 1

        await bot.edit_message_text(
            chat_id=sent.chat.id,
            message_id=sent.message_id,
            text=f'Отправлено {sending}/{len(users)}'
        )
