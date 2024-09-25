from aiogram.types import Message, CallbackQuery

import os

from init import dp,bot


# фильтр сообщений
def is_bot_active():
    file_path = os.path.join('switch', 'is_active.txt')
    with open(file_path, "r") as file:
        content = file.read()
        return content != '1'


async def send_switch_msg(chat_id: int):
    text = f'‼️🛠️У нас идут технические работы по улучшению качества работы нашего бота‼️🛠️\n\n' \
           f'💈Для совершения обмена напишете нашему оператору - @operator_Infinity\n\n' \
           f'С уважением, команда The Infinity Exchange🧬'
    await bot.send_message(chat_id=chat_id, text=text)


# тормозит всё если бот отключен
@dp.message_handler(lambda x: is_bot_active(), content_types='any', state='*')
async def switch_bot(msg: Message):
    await send_switch_msg(msg.from_user.id)


@dp.callback_query_handler(lambda x: is_bot_active(), state='*')
async def cb_switch_bot(cb: CallbackQuery):
    await send_switch_msg(cb.from_user.id)

