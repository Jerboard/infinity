from aiogram.types import Message, CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart

import db
import keyboards as kb
import utils as ut
from init import dp, bot, log_error
from data import capcha_list
from enums import Key, CB


# @dp.message()
# async def temp(msg: Message):
#     print(msg.chat.title)
#     print(msg.chat.id)
#
#
# @dp.channel_post()
# async def temp(msg: Message):
#     print(msg.chat.title)
#     print(msg.chat.id)


# Команда старт
@dp.message(CommandStart())
async def com_start(msg: Message, state: FSMContext):
    await state.clear()

    if msg.from_user.is_bot:
        return

    user = await db.get_user_info(msg.from_user.id)
    if not user:
        # тут проходит капчу
        check_referrer = msg.text.split(' ')
        referrer = check_referrer[1] if len(check_referrer) == 2 else '0'
        await ut.send_capcha(chat_id=msg.chat.id, first_name=msg.from_user.first_name, referrer=referrer)

    elif user.ban:
        await msg.answer (
            'Ваш аккаунт заблокирован - по вопросам можете обратиться к  @manager_Infinity',
            reply_markup=ReplyKeyboardRemove ()
        )

    else:
        await db.add_user(user_id=msg.from_user.id, full_name=msg.from_user.full_name, username=msg.from_user.username)
        await ut.send_msg(msg_key=Key.START.value, chat_id=msg.chat.id, keyboard=kb.get_start_kb())


# проверяет капчу
@dp.callback_query(lambda cb: cb.data.startswith(CB.CAPCHA.value))
async def capcha(cb: CallbackQuery, state: FSMContext):
    _, suc, ref_code = cb.data.split(':')
    log_error(f'{cb.data}', with_traceback=False)
    await cb.message.delete()
    if suc == '1':
        referrer = await db.get_user_info(ref_code=ref_code)
        await db.add_user(
            user_id=cb.from_user.id,
            full_name=cb.from_user.full_name,
            username=cb.from_user.username,
            referrer=referrer.user_id if referrer else None
        )
        await ut.send_msg(msg_key=Key.START.value, chat_id=cb.message.chat.id, keyboard=kb.get_start_kb())
    else:
        await cb.answer('⚠️ Вы не прошли проверку', show_alert=True)
        await ut.send_capcha(
            chat_id=cb.message.chat.id, first_name=cb.from_user.first_name, referrer=ref_code
        )


# назад к первому экрану
@dp.callback_query(lambda cb: cb.data.startswith(CB.BACK_START.value))
async def back_com_start(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    # text = 'Выберите из кнопок ниже:'
    await ut.send_msg(
        msg_key=Key.START.value,
        chat_id=cb.message.chat.id,
        edit_msg=cb.message.message_id
        # keyboard=kb.get_start_kb()
    )


# назад к первому экрану
@dp.callback_query(lambda cb: cb.data.startswith(CB.CANCEL.value))
async def cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    # text = 'Выберите из кнопок ниже:'
    await cb.message.delete()
    await ut.send_msg(msg_key=Key.START.value, chat_id=cb.message.chat.id, keyboard=kb.get_start_kb())
