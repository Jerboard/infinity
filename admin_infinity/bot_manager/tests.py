import json
import asyncio
import requests


from django.test import TestCase
from datetime import datetime
from enums import Key, PaymentStatus
import random


# url: http://127.0.0.1:8000/api/v1/order-status
# payload: {'status': 'canceled', 'request_id': 1681, 'hash_request': ''}


# Выполняем POST-запрос
def start_test():
    url = 'http://127.0.0.1:8001/'
    endpoint = 'api/v1/order-status/'
    url += endpoint

    payload = {
        # 'status': PaymentStatus.CANCELED.value,
        'status': PaymentStatus.SUCCESS.value,
        'request_id': 15,
        'hash_request': 'ntest'
    }

    print(url)
    print(payload)
    response = requests.post(url, json=payload)
    print(response.text)
    r = response.json()
    if r['success']:
        print(r)

    else:
        print(r)


if __name__ == '__main__':
    start_test()
    # asyncio.run(stress_test())
