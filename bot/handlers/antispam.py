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
from enums import CB, UserStatus, Key


# Отправьте сообщение в антиспам
@dp.callback_query(lambda cb: cb.data.startswith(CB.ANTISPAM.value))
async def antispam(cb: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatus.ANTISPAM)
    await state.update_data(data={'message_id': cb.message.message_id})
    await ut.send_msg(
        msg_key=Key.ANTISPAM.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        keyboard=kb.get_back_kb(CB.BACK_START.value)
    )


# Отправьте сообщение в антиспам для админа
@dp.callback_query(lambda cb: cb.data.startswith(CB.ADMIN_ANTISPAM.value))
async def antispam(cb: CallbackQuery, state: FSMContext):
    await state.set_state(UserStatus.ANTISPAM)
    await state.update_data(data={'message_id': cb.message.message_id})
    # await cb.message.edit_reply_markup(reply_markup=kb.)


# приём сообщения
@dp.message(StateFilter(UserStatus.ANTISPAM))
async def antispam_send(msg: Message, state: FSMContext):
    data = await state.get_data()

    await ut.send_any_message(
        msg=msg,
        chat_id=Config.antispam_chat,
        keyboard=kb.get_antispam_kb(user_id=data.get('user_id', msg.from_user.id))
    )
