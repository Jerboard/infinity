from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from typing import Optional
from enum import Enum
import logging
import json

from bot_manager.models import Order


class PaymentStatus(Enum):
    PROC = "processing"
    SUCCESS = "success"
    NO_FUNDS = "no_funds"
    CANCELED = "canceled"
    WAITING = "waiting"
    ERROR = "error"


# принимает отмену от сервера
@csrf_exempt
def close_order_api(request: HttpRequest) -> JsonResponse:
    try:
        request_data: dict = json.loads(request.body)

        request_id = int(request_data['request_id'])
        order = Order.objects.filter(request_id=request_id).first()

        if request_data.get('status') == PaymentStatus.CANCELED.value:
            order.status = 'cancel'
            order.save()
            return JsonResponse({'success': 1})

        elif request_data.get('status') == PaymentStatus.SUCCESS.value and request_data.get('hash_request'):
            order.hash = request_data['hash_request']
            order.status = 'processing'
            order.save()
            return JsonResponse({'success': 1})

        else:
            return JsonResponse({'success': 0})

    except Exception as ex:
        logging.warning(ex)
        return JsonResponse({'success': 0})

