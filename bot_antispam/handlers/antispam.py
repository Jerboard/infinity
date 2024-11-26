from aiogram.types import Message, CallbackQuery
from aiogram.enums.content_type import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, CommandStart

from datetime import datetime, timedelta, timezone
from asyncio import sleep

import db
import keyboards as kb
import utils_antispam as ut
from config import Config
from init import dp, bot, log_error
from enums import CB, UserStatus, Key, Action


# Антиспам старт
@dp.message(CommandStart())
async def antispam_start(msg: Message, state: FSMContext):
    await state.clear()
    # await ut.antispam_sent(cb.message, edit_msg=cb.message)
    await ut.send_msg(
        msg_key=Key.ANTISPAM.value,
        chat_id=msg.chat.id,
    )


# Отправьте сообщение в антиспам для админа
@dp.callback_query(lambda cb: cb.data.startswith(CB.ADMIN_ANTISPAM.value))
async def antispam_listen(cb: CallbackQuery, state: FSMContext):
    _, action, for_user_str = cb.data.split(':')
    for_user = int(for_user_str)

    await state.set_state(UserStatus.ANTISPAM)

    await cb.message.edit_reply_markup(reply_markup=kb.get_antispam_admin_kb(for_user, on=False))
    await state.update_data(data={'message_id': cb.message.message_id, 'for_user': for_user})

    # if cb.from_user.id == Config.antispam_chat:
    #     await cb.message.edit_reply_markup(reply_markup=kb.get_antispam_admin_kb(for_user, on=False))
    #     await state.update_data(data={'message_id': cb.message.message_id, 'for_user': for_user})

    # else:
    #     text = (f'Приветствую, {cb.from_user.full_name}!\n\n'
    #             f'Это антиспам бот INFINITY EXCHANGE (если не можешь писать первым)\n'
    #             f'Поддержка ежедневно 24/7')
    #     sent = await cb.message.answer(text, reply_markup=kb.get_cancel_kb())
    #     await state.update_data(data={'message_id': sent.message_id, 'for_user': for_user})
    # await cb.message.edit_reply_markup(reply_markup=kb.)


# приём сообщения
@dp.message()
async def antispam_send(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    # отправка ответа от админа
    if msg.from_user.id == Config.antispam_chat:
        try:
            await bot.edit_message_reply_markup(
                chat_id=msg.chat.id,
                message_id=data['message_id'],
                reply_markup=kb.get_antispam_admin_kb(data['for_user'])
            )
            await ut.send_any_message(
                msg=msg,
                chat_id=data['for_user'],
            )
        except Exception as ex:
            await msg.answer('❗️ Сообщение не отправлено')

    # отправка ответа от пользователя
    else:
        last_msg = await db.get_last_msg(user_id=msg.from_user.id)
        now = datetime.now(Config.tz)
        minute_ago = now - timedelta(minutes=1)

        if last_msg and last_msg.last_sent > minute_ago:
            different = last_msg.last_sent - minute_ago
            next_msg = now + different
            sent = await msg.answer(f'❌ Вы не можете отправлять сообщение раньше чем раз в минуту\n'
                                    f'Следующее сообщение в {next_msg.time().replace(microsecond=0)} мск')
            await sleep(different.seconds)
            await sent.delete()

        else:
            name = f'{msg.from_user.full_name} (@{msg.from_user.username})' if msg.from_user.username else msg.from_user.full_name
            await bot.send_message(chat_id=Config.antispam_chat, text=f'От {name}')
            await ut.send_any_message(
                msg=msg,
                chat_id=Config.antispam_chat,
                keyboard=kb.get_antispam_admin_kb(user_id=msg.from_user.id)
            )
            await db.update_last_msg(user_id=msg.from_user.id)
            await msg.answer('Ваше сообщение отправлено, ожидайте ответа поддержки')
