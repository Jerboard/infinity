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
from enums import CB, UserStatus, Key, Action


# Отправьте сообщение в антиспам
@dp.callback_query(lambda cb: cb.data.startswith(CB.ANTISPAM.value))
async def antispam(cb: CallbackQuery, state: FSMContext):
    # await state.set_state(UserStatus.ANTISPAM)
    # await state.update_data(data={'message_id': cb.message.message_id})
    await ut.send_msg(
        msg_key=Key.ANTISPAM.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id,
        keyboard=kb.get_antispam_user_kb()
    )


# Отправьте сообщение в антиспам для админа
@dp.callback_query(lambda cb: cb.data.startswith(CB.ADMIN_ANTISPAM.value))
async def antispam_listen(cb: CallbackQuery, state: FSMContext):
    _, action, for_user_str = cb.data.split(':')
    for_user = int(for_user_str)

    if action == Action.SEND:
        await state.set_state(UserStatus.ANTISPAM)

        if cb.from_user.id == Config.antispam_chat:
            await cb.message.edit_reply_markup(reply_markup=kb.get_antispam_admin_kb(for_user, on=False))
            await state.update_data(data={'message_id': cb.message.message_id, 'for_user': for_user})

        else:
            text = (f'Приветствую, {cb.from_user.full_name}!\n\n'
                    f'Это антспам бот INFINITY EXCHANGE (если не можешь писать первым)\n'
                    f'Поддержка ежедневно 24/7')
            sent = await cb.message.answer(text, reply_markup=kb.get_cancel_kb())
            await state.update_data(data={'message_id': sent.message_id, 'for_user': for_user})
    # await cb.message.edit_reply_markup(reply_markup=kb.)


# приём сообщения
@dp.message(StateFilter(UserStatus.ANTISPAM))
async def antispam_send(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    if msg.from_user.id == Config.antispam_chat:
        await bot.edit_message_reply_markup(
            chat_id=msg.chat.id,
            message_id=data['message_id'],
            reply_markup=kb.get_antispam_admin_kb(data['for_user'])
        )
        await ut.send_any_message(
            msg=msg,
            chat_id=data['for_user'],
        )

    else:
        await bot.delete_message(chat_id=msg.chat.id, message_id=data['message_id'])
        await ut.send_any_message(
            msg=msg,
            chat_id=data['for_user'],
            keyboard=kb.get_antispam_admin_kb(user_id=data.get('user_id', msg.from_user.id))
        )
