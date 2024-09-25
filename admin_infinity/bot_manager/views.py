from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout

import os
import logging

from datetime import datetime
from .export_file import export
from . import utils_bot as ut
from .models import Order, Currency, PayMethod, Promo, User, CashbackLevel, CashbackOrder


page_list = [{'name': 'Новые', 'page': 'new_orders'},
             {'name': 'Обработанные', 'page': 'closed_orders'},
             {'name': 'Кошельки и оплата', 'page': 'pay_setting'},
             {'name': 'Промокоды', 'page': 'promo_setting'},
             {'name': 'Выключатель', 'page': 'switch'},
             {'name': 'Выйти', 'page': 'logout'}]


# первая страница
def home_page_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return redirect('new_orders')


# вход
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('new_orders')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# выход
def logout_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        logout(request)
        return redirect('login')


# новые заказы
def new_orders_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        # вносим изменения в заказ
        ut.proc_order(request.POST)

        return redirect('new_orders')
    else:
        orders = Order.objects.filter(status='new')
        cashback_orders = CashbackOrder.objects.filter(status='new')

        context = {
            'pages': page_list,
            'this_page': page_list[0]['name'],
            'orders': orders,
            'count_new_orders': len(orders),
            'cashback_orders': cashback_orders,
            'count_cashback': len(cashback_orders)
        }
        return render(request, 'new_orders.html', context)


# закрытые заказы
def old_orders_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if request.method == 'POST':
            data = request.POST
            # print(f'>>>>>data\t{data}')
            if data['button'] == 'refresh':
                return redirect('closed_orders')

            orders = Order.objects.all()
            dateFrom = ''
            if data['from'] != '':
                dateFrom = datetime.strptime(data['from'], "%Y-%m-%d")
                orders = orders.filter(time__gt=data['from'])
            if data['to'] != '':
                orders = orders.filter(time__lt=data['to'])
            if data['user'] != '':
                if data['user'].isdigit() == True:
                    orders = orders.filter(user_id=data['user'])
                else:
                    orders = orders.filter(name_user=data['user'])
            if data['coin'] != '':
                orders = orders.filter(coin=data['coin'].upper())
            if data['wallet'] != '':
                orders = orders.filter(wallet=data['wallet'])
            if data['promo'] != '':
                orders = orders.filter(promo=data['promo'])
            if data['hash'] != '':
                orders = orders.filter(hash=data['hash'])

            if data['button'] == 'filter':
                context = {
                    'pages': page_list,
                    'this_page': page_list[1]['name'],
                    'orders': orders,
                    'today': datetime.now().date(),
                    'fFrom': dateFrom,
                    'fUser': data['user'],
                    'fCoin': data['coin'],
                    'fWallet': data['wallet'],
                    'fPromo': data['promo'],
                    'fHash': data['hash']
                }

                return render(request, 'closed_orders.html', context)

            if data['button'] == 'export':
                export(orders)

            return redirect('closed_orders')

        else:
            orders = Order.objects.all().order_by('-id')[:50]

            context = {
                'pages': page_list,
                'this_page': page_list[1]['name'],
                'orders': orders,
                'today': datetime.now().date()
            }
            return render(request, 'closed_orders.html', context)


# кошельки и способы оплаты
def wallets_and_pay_methods_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if request.method == 'POST':
            data = request.POST
            if data.get("type") == 'currency':
                currency = Currency.objects.get(id=data['id'])
                currency.min = float(data['min_sum'].replace(',', '.')) if data['min_sum'] is not None else 0
                currency.max = float(data['max_sum'].replace(',', '.')) if data['max_sum'] is not None else 0
                currency.ratio = float(data['percent'].replace(',', '.')) if data['percent'] is not None else 0
                currency.commission = float(data['com'].replace(',', '.')) if data['com'] is not None else 0
                currency.buy_price = float(data['buy'].replace(',', '.')) if data['buy'] is not None else 0
                is_active = int(data.get('active', 0)) if data.get('active', 0) != 'on' else 1
                currency.is_active = is_active
                currency.round = int(data['round'])
                currency.save()

            elif data.get("type") == 'pay_method':
                pay_method = PayMethod.objects.get(id=data['id'])
                if data['button'] == 'del':
                    pay_method.delete()
                else:
                    pay_method.name = data['bank']
                    pay_method.card = data['card']
                    is_active = int(data.get('active', 0)) if data.get('active', 0) != 'on' else 1
                    pay_method.is_active = is_active
                    pay_method.save()

            elif data.get("type") == 'add':
                pay_method = PayMethod()
                pay_method.name = ''
                pay_method.card = ''
                pay_method.is_active = 0
                pay_method.save()

            return redirect('pay_setting')

        else:
            currencies = Currency.objects.all()
            pay_methods = PayMethod.objects.all()

            context = {
                'pages': page_list,
                'this_page': page_list[2]['name'],
                'currencies': currencies,
                'pay_methods': pay_methods,
            }

            return render(request, 'pay_setting.html', context)


# Промокоды
def promo_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if request.method == 'POST':
            data = request.POST
            print(data)
            if data['type'] == 'codes':
                promo = Promo.objects.get(id=data['id'])
                if data['button'] == 'del':
                    promo.delete()
                else:
                    try:
                        promo.promo = data['promo']
                        promo.rate = data['rate']
                        promo.start_date = data['date_start'] if data['date_start'] != '' else None
                        promo.end_date = data['date_end'] if data['date_end'] != '' else None
                        promo.many = data['count']
                        is_active = int(data.get('active', 0)) if data.get('active', 0) != 'on' else 1
                        promo.is_active = is_active
                        is_onetime = int(data.get('onetime', 0)) if data.get('onetime', 0) != 'on' else 1
                        promo.is_onetime = is_onetime
                        promo.save()
                    except:
                        pass

            elif data.get("type") == 'add':
                promo = Promo()
                promo.promo = ''
                promo.rate = 0
                promo.start_date = None
                promo.end_date = None
                promo.many = 0
                promo.is_active = 0
                promo.save()

            elif data['type'] == 'levels':
                level = CashbackLevel.objects.get(id=data['id'])
                level.count_users = data['count']
                level.percent = data['percent'].replace(',', '.')
                level.save()

            return redirect('promo_setting')

        else:
            promo = Promo.objects.all()
            levels = CashbackLevel.objects.all()
            context = {
                'pages': page_list,
                'this_page': page_list[3]['name'],
                'promo': promo,
                'levels': levels,
            }
            return render(request, 'promo_setting.html', context)


# Выключатель
def switch_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        file_path = os.path.join('home', 'bot', 'data', 'is_active.txt')
        # file_path = os.path.join('is_active.txt')
        with open(file_path, "r") as file:
            position = file.read()
        if request.method == 'POST':
            data = request.POST
            position = int(data['position'])
            with open(file_path, "w") as file:
                file.write(data['position'])

        context = {'pages': page_list,
                   'this_page': page_list[4]['name'],
                   'position': position
                   }
        return render(request, 'switch.html', context)

