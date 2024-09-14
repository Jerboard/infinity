from aiogram.types import Message, InlineKeyboardMarkup, InputMediaPhoto, FSInputFile
from aiogram.fsm.context import FSMContext
from asyncio import sleep
from random import choice

import db
import keyboards as kb
from init import bot
from config import Config
from data import capcha_list
import utils as ut
from enums import Key


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


# временное сообщение
async def send_time_message(chat_id: int, text: str) -> None:
    sent = await bot.send_message(chat_id=chat_id, text=text)
    await sleep(3)
    await sent.delete()


# обрабатывает текст. заменяет неподдерживаемые теги
def parse_text(text: str) -> str:
    return (text.replace('<br>', '\n')

            )
    # return text


# отправляет сообщение
async def send_msg(
        chat_id: int,
        msg_key: str = None,
        msg_data: db.MsgRow = None,
        text: str = None,
        edit_msg: int = None,
        keyboard: InlineKeyboardMarkup = None
) -> Message:
    # если тест, чтоб возвращал тестовую картинку
    # if Config.debug:
        # msg_key = Config.test_photo
        # msg_key = 'test'

    if not msg_data:
        msg_data = await db.get_msg(msg_key)

    # если фото обновлено и не имеет своего ключа
    # if Config.debug:
    #     photo_id = Config.test_photo
    #     update = False
    if msg_data.photo_id and msg_data.bot_id == Config.bot_id:
        photo_id = msg_data.photo_id
        update = False
    else:
        photo_id = FSInputFile(msg_data.photo_path)
        update = True

    print(text)
    text = parse_text(text) if text else parse_text(msg_data.text)

    if edit_msg:
        photo = InputMediaPhoto(media=photo_id, caption=text)
        sent = await bot.edit_message_media(
            chat_id=chat_id,
            message_id=edit_msg,
            media=photo,
            reply_markup=keyboard
        )

    else:
        sent = await bot.send_photo(
            chat_id=chat_id,
            photo=photo_id,
            caption=text,
            reply_markup=keyboard
        )

    if update:
        await db.update_msg(msg_data.id, photo_id=sent.photo[-1].file_id, bot_id=Config.bot_id)

    return sent


# считает сумму
# async def check_info_output(state: FSMContext, del_msg: bool = False):
#     data = await state.get_data()
#     currency = await db.get_currency(data['currency_id'])
#
#     text = ut.get_check_info_text(data=data, currency=currency)
#     if del_msg:
#         await bot.delete_message(chat_id=data['user_id'], message_id=data['message_id'])
#         sent = await ut.send_msg(
#             msg_key=Key.CHECK_WALLET.value,
#             chat_id=data['user_id'],
#             text=text,
#             keyboard=kb.get_check_info_kb(use_points=data['used_points'], points=data['points'], promo=data.get('promo'))
#         )
#         await state.update_data(data={'message_id': sent.message_id})
#     else:
#         await ut.send_msg(
#             msg_key=Key.CHECK_WALLET.value,
#             chat_id=data['user_id'],
#             edit_msg=data['message_id'],
#             text=text,
#             keyboard=kb.get_check_info_kb(use_points=data['used_points'], points=data['points'], promo=data.get('promo'))
#         )


async def main_exchange(state: FSMContext, del_msg: bool = False):
    data = await state.get_data()
    # currency_rate = data['rate']
    # sum_coin = data['sum_exchange']
    # currency_code = data['currency_code']
    # sum_rub = data['amount']
    # balance = f'<s>{data["balance"]}</s>' if data.get('used_balance') else data['balance']
    # pay_string = data['pay_string']

    # for k, v in data.items():
    #     print(f'{k}: {v}')

    # text = (
    #     f'Средний рыночный курс: {currency_rate}\n\n'
    #     f'Данный курс не учитывает комиссии сервиса\n\n'
    #     f'Вы получите: {sum_coin} {currency_code} ~ {sum_rub} RUB\n\n'
    #     f'Внутренний баланс кошелька: {balance} RUB\n\n'
    #     f'{pay_string}'
    # )
    msg_data = await db.get_msg(Key.EXCHANGE.value)
    text = msg_data.text.format(
        currency_rate=data['rate'],
        sum_coin=data['sum_exchange'],
        currency_code=data['currency_code'],
        sum_rub=data['amount'],
        balance=f'<s>{data["balance"]}</s>' if data.get('used_balance') else data['balance'],
        pay_string=data['pay_string']
    )

    # print(f'text:\n{text}')
    if del_msg:
        await bot.delete_message(chat_id=data['user_id'], message_id=data['message_id'])
        edit_msg = None
    else:
        edit_msg = data['message_id']
    sent = await ut.send_msg(
        msg_data=msg_data,
        chat_id=data['user_id'],
        edit_msg=edit_msg,
        text=text,
        keyboard=kb.get_main_exchange_kb(total_amount=data['total_amount'], promo_id=data.get('promo_id'))
    )
    await state.update_data(data={'message_id': sent.message_id})
