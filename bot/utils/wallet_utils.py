import re
import hashlib
import base58
import bech32
import coinaddrvalidator

from datetime import datetime

import db
from config import Config
from enums import Coin, OrderStatus

import random
import string


trash_orders_id = [1, 2, 3, 13, 24, 19, 7, 4, 5, 6, 8, 15, 10, 16, 22, 25, 29, 28, 26, 31, 45, 48, 63, 2849]


def remove_random_char(s):
    # Проверка, чтобы строка была длиннее 5 символов и чтобы был доступный символ для удаления
    if len(s) <= 5:
        return s  # Возвращаем исходную строку, если нельзя удалить

    # Генерируем случайный индекс от 5 до конца строки
    index = random.randint(5, len(s) - 1)
    # Удаляем символ по этому индексу
    return s[:index] + s[index + 1:]


def add_random_char(s):
    # Генерируем случайный символ для добавления
    random_char = random.choice(string.ascii_letters + string.digits)

    # Генерируем случайный индекс от 5 до конца строки
    index = random.randint(5, len(s))

    # Вставляем случайный символ в случайное место
    return s[:index] + random_char + s[index:]


async def test_wallet_valid():
    start_time = datetime.now()
    orders = await db.get_orders(status=OrderStatus.SUC.value)
    counter = 0
    exceptions = []
    for order in orders:
        if order.id in trash_orders_id:
            continue
        wallet = order.wallet
        for i in range(5):
            wallet = remove_random_char(wallet)
        for i in range(5):
            wallet = add_random_char(wallet)
        result = check_valid_wallet(coin=order.coin, wallet=wallet)
        if result:
            counter += 1
        else:
            # print(order.coin)
            exceptions.append(order.coin)

    all_orders = len(orders) - len(trash_orders_id)
    print('---')
    # print(exceptions)
    print(f'{counter}/{all_orders}')
    print(f'{round((counter / all_orders) * 100, 2)} %')
    delta = datetime.now() - start_time
    print(delta)
    print(delta / len(orders))


# проверяет кошелёк
def check_valid_wallet(coin: str, wallet: str) -> bool:
    if Config.debug:
        return True

    if coin == Coin.BTC:
        return validate_bitcoin_address(wallet)

    elif coin == Coin.LTC:
        return validate_litecoin_wallet(wallet)

    elif coin == Coin.XMR:
        return validate_monero_address(wallet)

    elif coin == Coin.USDT:
        return validate_usdt_address(wallet)

    else:
        return False


# проверка бтк адресов
def validate_bitcoin_address(address):
    # Проверка формата P2PKH и P2SH (base58)
    if re.match(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", address):
        # return validate_base58_address(address)
        try:
            # Декодируем base58
            decoded = base58.b58decode(address).hex()

            # Разделяем на части: префикс, публичный ключ и контрольная сумма
            prefix_and_hash = decoded[:-8]
            checksum = decoded[-8:]

            # Проверяем контрольную сумму
            hash1 = hashlib.sha256(bytes.fromhex(prefix_and_hash)).hexdigest()
            hash2 = hashlib.sha256(bytes.fromhex(hash1)).hexdigest()

            # Адрес валиден, если контрольная сумма совпадает
            return hash2[:8] == checksum
        except Exception:
            return False

    # Проверка формата Bech32 (SegWit)
    if address.startswith(('bc1', 'tb1', 'bcrt1', 'ltc1')) and len(address) >= 26 and len(address) <= 90:
        try:
            hrp, data = bech32.bech32_decode(address)
            # Проверяем, что это адрес с hrp 'bc' (основная сеть)
            if hrp != 'bc' or not data:
                if not address.islower():
                    return False

                if len(address) > 74:
                    return False

                valid_chars = set("023456789acdefghjklmnpqrstuvwxyz")
                data_part = address[address.index('1') + 1:]
                if not all(c in valid_chars for c in data_part):
                    return False

                return True
            # Проверяем длину и корректность данных
            return data is not None
        except Exception:
            return False
        # return validate_bech32_address(address)

    # Если не совпало с форматами
    return False


# проверка лтк через ре
def validate_litecoin_wallet(address: str) -> bool:
    # легаси P2PKH и P2SH
    # if address[0] in ['L', 'M']:
    if re.match(r"^[LM3][a-km-zA-HJ-NP-Z1-9]{26,34}$", address):
        return True

    elif re.match(r"^3[a-km-zA-HJ-NP-Z1-9]{25,33}$", address):
        return True

    elif re.match(r"^ltc1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{39,87}$", address):
        return True

    else:
        return False


# проверяем монеро по длине и первому символу
def validate_monero_address(address: str) -> bool:
    # Monero-адреса обычно имеют длину 95 символов для стандартного адреса
    if len(address) not in (95, 106):
        return False

    # Проверка начального символа: для Monero это "4" или "8"
    if address[0] not in ('4', '8'):
        return False

    return True


# проверяем юсдт через ре
def validate_usdt_address(address: str) -> bool:
    if re.match(r"^T[a-km-zA-HJ-NP-Z1-9]{33}$", address):
        return True
    else:
        return False


# Пример использования
def test_btc():
    test_addresses = [
        'ltc1qvpycwysyf6tr8y2dc79jngsv6eq0fpgu0qr6h5',
        "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4",
        "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqzk5jj0",
        "bc1invalid",
        "bc1qw4v9rrr7spdx6k5zup8hvf7y38hz0q4au79tg3",  # bech32
        "bc1p2x9ewv4nkyll2xx2avfhckzay4hx7xw7x5rzd5"  # bech32m
    ]

    for addr in test_addresses:
        # validate_bitcoin_cost(addr)
        print(validate_bitcoin_address(addr))


def test_ltc():
    test_addresses = [
        'LZ8MGZyRK7phBRUKu6kzPgygD6wno63Z3f',  # True Legacy P2PKH
        'ltc1qyzdp36upxdhk4tpzvqjq4z37qzwykmvh5v4l9g',   # True Bech32
        'LWttPMKz3YxBDuFRi4K8cRq8cYxkmFfge2',
        'MPoUJ5MT7zX6UweR2e3kyt4W9yBbaKnRC2',
        'DPoUJ5MT7zX6UweR2e3kyt4W9yBbaKnRC2',
        'LcRKWHDLfjeJKJ6DzDPZxuX41Abq6kB1Sj'
    ]

    for addr in test_addresses:
        print(validate_litecoin_wallet(addr))


# test_ltc()


def test_xmr():
    test_addresses = [
        '86MoiGnUfZYNbcwBMrJTVRHBahJ7LRQKxVoP7HewaBqX8ZPnUnq4uUcXLgofbbP1C66vNBaypEnjf7aUr8GSxHpVHkqhiRm',
        '4Jp3Xz9LvoSU73cuKaVhDDEPo7swqkxhKgP8UiLeubgsNJDYRTPWQDugfpa5KauYBEV52bi33NdHTLdRnYqkWvB76gW7m6UQ7uzBWbaN78',
        '4Jp3Xz9LvoSU73cuKaVhDDEPo7swqkxhKgP8UiLeubgsNJDYRTPWQDugfpa5KauYBEV52bi33NdHTLdRnYqkWvB76b2RrNDwTjpGm5LePt',
        '8ATUry2Vnt4AHo5TXPrhbCByXzUN5UbiC9nNWmshJv3aDoJagtAJwz3amVKY4q5HN8FQJc93p9LF1FdXgyFUdYN3V4C62Nw'
    ]

    for addr in test_addresses:
        print(validate_monero_address(addr))


# test_xmr()


def test_usdt():
    test_addresses = [
        '0x117811FDC3CC207Fe121a025b1ab7f27C163707C',
        'TB3oMkCgkZnXyyZhxZ4uEYHQ3BQknFJcuf',
        'LcRKWHDLfjeJKJ6DzDPZxuX41Abq6kB1Sj',
        'TMAB6HgLCtAjAVRtgFoCUKHP1prcr8fRim'

    ]

    for addr in test_addresses:
        print(validate_usdt_address(addr))

# test_usdt()

# старые адреса бтк P2PKH и P2SH
# def validate_base58_address(address):
#     try:
#         # Декодируем base58
#         decoded = base58.b58decode(address).hex()
#
#         # Разделяем на части: префикс, публичный ключ и контрольная сумма
#         prefix_and_hash = decoded[:-8]
#         checksum = decoded[-8:]
#
#         # Проверяем контрольную сумму
#         hash1 = hashlib.sha256(bytes.fromhex(prefix_and_hash)).hexdigest()
#         hash2 = hashlib.sha256(bytes.fromhex(hash1)).hexdigest()
#
#         # Адрес валиден, если контрольная сумма совпадает
#         return hash2[:8] == checksum
#     except Exception:
#         return False


# проверяем Bech32 тут для битка
# def validate_bech32_address(address):
#     try:
#         hrp, data = bech32.bech32_decode(address)
#         # Проверяем, что это адрес с hrp 'bc' (основная сеть)
#         if hrp != 'bc' or not data:
#             if not address.islower():
#                 return False
#
#             if len(address) > 74:
#                 return False
#
#             valid_chars = set("023456789acdefghjklmnpqrstuvwxyz")
#             data_part = address[address.index('1') + 1:]
#             if not all(c in valid_chars for c in data_part):
#                 return False
#
#             return True
#         # Проверяем длину и корректность данных
#         return data is not None
#     except Exception:
#         return False

