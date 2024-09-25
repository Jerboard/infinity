from aiogram.types import Message, CallbackQuery
from aiogram.enums.content_type import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from datetime import datetime

import db
import keyboards as kb
import utils as ut
from config import Config
from init import dp, bot, log_error
from enums import CB, UserStatus, Key, MainButton


# Раздел "О нас"
async def info_send(msg: Message, edit_msg: int = None):
    await ut.send_msg(
        msg_key=Key.INFO.value,
        chat_id=msg.chat.id,
        edit_msg=edit_msg,
        keyboard=kb.get_info_kb()
    )


# старт обмена инлайн
@dp.callback_query(lambda cb: cb.data.startswith(CB.INFO.value))
async def info_send_inline(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await info_send(cb.message, edit_msg=cb.message)


# старт обмена кнопка
@dp.message(lambda msg: msg.text == MainButton.INFO.value)
async def info_send_reply(msg: Message, state: FSMContext):
    await state.clear()
    await info_send(msg)


# отправить отзыв
@dp.callback_query(lambda cb: cb.data.startswith(CB.FEEDBACK.value))
async def feedback(cb: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatus.FEEDBACK)

    text = 'Оставьте отзыв о нашей работе'
    sent = await cb.message.answer(text, reply_markup=kb.get_cancel_kb())
    await state.update_data(data={'message_id': sent.message_id})


# Отправляет отзыв на модерацию
@dp.message(StateFilter(UserStatus.FEEDBACK))
async def take_feedback(msg: Message, state: FSMContext):
    if msg.content_type != ContentType.TEXT:
        await msg.answer('Отправьте текстовое сообщение')
        return

    data = await state.get_data()
    await state.clear()

    await bot.delete_message(chat_id=msg.chat.id, message_id=data['message_id'])
    await bot.send_message(
        chat_id=Config.access_chat,
        text=msg.text,
        entities=msg.entities,
        parse_mode=None,
        reply_markup=kb.get_feedback_kb()
    )
    await msg.answer('Благодарим за отзыв и бла-бла-бла')


# публикует отзыв
@dp.callback_query(lambda cb: cb.data.startswith(CB.PUBLISH_FEEDBACK.value))
async def publish_feedback(cb: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=cb.message.chat.id, message_id=cb.message.message_id)

    await bot.send_message(
        chat_id=Config.feedback_chat,
        text=cb.message.text,
        entities=cb.message.entities,
        parse_mode=None
    )