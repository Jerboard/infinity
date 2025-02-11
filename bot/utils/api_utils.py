import aiohttp
import typing as t

from datetime import datetime

from init import log_error
from config import Config
from enums import Key


# Выполняем POST-запрос
async def get_details_api(request_id: int, amount: int, method_type: str) -> t.Optional[dict]:
    try:
        body = {
            'internal_id': request_id,
            'amount': amount,
            'service_name': 'test',
            'method_type': method_type
        }
        print("Отправляем тело запроса:", body)

        # Открываем сессию aiohttp
        async with aiohttp.ClientSession() as session:
            url = f"{Config.api_url}{Config.endpoint_details}"
            async with session.post(url, json=body) as response:
                r = await response.json()
                print(r)

                if r.get('success'):
                    return r

    except Exception as ex:
        log_error(ex)


# Завершаем реквизиты
async def close_detail_api(request_id: int, amount: int, status: str) -> t.Optional[dict]:
    body = {
        'id': request_id,
        'internal_id': 1,
        'amount': amount,
        'service_name': 'test',
        'status': status
    }
    print(body)

    try:
        # Открываем сессию aiohttp
        async with aiohttp.ClientSession() as session:
            url = f"{Config.api_url}{Config.endpoint_close}"
            print(f'url: {url}')
            async with session.post(url, json=body) as response:
                print(response.text)
                r = await response.json()
                print(r)

                if r.get('success'):
                    return r

    except Exception as ex:
        log_error(ex)
