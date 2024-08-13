from aiogram.types import Message, CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart

import db
import keyboards as kb
import utils as ut
from init import dp, bot
from enums import Key


# Команда старт
@dp.message(CommandStart())
async def com_start(msg: Message, state: FSMContext):
    await state.clear()

    if msg.from_user.is_bot:
        return

    user = await db.get_user_info(msg.from_user.id)
    if not user:
        # тут проходит капчу
        # check_referrer = msg.text.split(' ')
        # referrer = check_referrer[1] if len(check_referrer) == 2 else None
        pass

    elif user.ban:
        await msg.answer (
            'Ваш аккаунт заблокирован - по вопросам можете обратиться к  @manager_Infinity',
            reply_markup=ReplyKeyboardRemove ()
        )
        return

    await db.add_user(user_id=msg.from_user.id, full_name=msg.from_user.full_name, username=msg.from_user.username)
    await ut.send_msg(msg_key=Key.START.value, chat_id=msg.chat.id, kb=kb.get_start_kb())


# назад к первому экрану
@dp.callback_query_handler(text_startswith='back_start', state='*')
async def back_com_start(cb: CallbackQuery, state: FSMContext):
    await state.finish()

    text = 'Выберите из кнопок ниже:'
    photo_id = photos['start']
    photo = InputMediaPhoto(photo_id, text)
    try:
        await cb.message.edit_media(media=photo)
    except:
        await cb.message.delete()
        await cb.message.answer_photo(photo=photo_id, caption=text)


# выбор валюты
@dp.message_handler(text=['📚 Поддержка'], state='*')
async def support(msg: Message, state: FSMContext):
    await state.finish()

    user = get_user_data (msg.from_user.id)
    if user ['ban']:
        await msg.answer ('Ваш аккаунт заблокирован - по вопросам можете обратиться к  @manager_Infinity',
                          reply_markup=ReplyKeyboardRemove ())
        return

    text = '📍 Тут собраны ответы на самые распространенные вопросы, а также наши контактные данные.'
    photo_id = photos ['support']

    await msg.answer_photo(photo=photo_id, caption=text, reply_markup=get_support_kb())


# удалить
# @dp.message_handler(content_types=['photo'], state='*')
# async def save_photo(msg: Message):
#     # logging.warning(f'{msg.caption}: {msg.photo[-1].file_id}')
#     print(msg.photo[-1].file_id)


from init import dp
