import re
import hashlib
import base58
import bech32
import coinaddrvalidator


def validate_bitcoin_address(address):
    # Проверка формата P2PKH и P2SH (base58)
    if re.match(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", address):
        return validate_base58_address(address)

    # Проверка формата Bech32 (SegWit)
    if address.startswith("bc1") and len(address) >= 26 and len(address) <= 90:
        return validate_bech32_address(address)

    # Если не совпало с форматами
    return False


def validate_base58_address(address):
    """Проверка адресов P2PKH и P2SH"""
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


def validate_bech32_address(address):
    """Проверка Bech32 (SegWit) адресов"""
    try:
        hrp, data = bech32.bech32_decode(address)
        print(hrp, data)
        # Проверяем, что это адрес с hrp 'bc' (основная сеть)
        if hrp != 'bc':
            return False
        # Проверяем длину и корректность данных
        return data is not None
    except Exception:
        return False


def validate_bech32_address_1(address):
    """Проверка Bech32 (SegWit) адресов с учетом Witness Version и Witness Program"""
    try:
        # Декодируем Bech32-адрес
        hrp, data = bech32.bech32_decode(address)
        print(hrp, data)
        if hrp != 'bc':
            return False

        # Проверяем Witness Version (первая часть данных)
        witness_version = data[0]
        if witness_version < 0 or witness_version > 16:
            return False

        # Проверка длины Witness Program для SegWit адресов
        witness_program = data[1:]
        witness_program_length = len(witness_program)
        if witness_version == 0 and (witness_program_length != 20 and witness_program_length != 32):
            return False
        elif witness_version > 0 and (witness_program_length < 2 or witness_program_length > 40):
            return False

        return True
    except Exception:
        return False


# от клауд
def is_valid_bech32_cl(addr):
    if not addr.startswith('bc1'):
        return False

    try:
        # Проверяем длину
        if len(addr) < 14 or len(addr) > 74:
            return False

        # Проверяем допустимые символы
        allowed_chars = set("023456789acdefghjklmnpqrstuvwxyz")
        if not all(c in allowed_chars for c in addr[3:]):
            return False

        return True
    except Exception:
        return False


# Примеры использования
# print(validate_bitcoin_address("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"))  # P2PKH адрес
# print(validate_bitcoin_address("3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"))  # P2SH адрес
# print(validate_bitcoin_address("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080"))  # Bech32 адрес
# print(validate_bech32_address("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080"))  # Bech32 адрес
# print(validate_bech32_address_1("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080"))  # Bech32 адресprint(validate_bech32_address("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080"))  # Bech32 адрес
print(is_valid_bech32_cl("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080"))  # Bech32 адрес

# print(validate_bitcoin_address("ltc1qvpycwysyf6tr8y2dc79jngsv6eq0fpgu0qr6h5"))  # Bech32 адрес
