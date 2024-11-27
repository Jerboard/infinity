from datetime import timedelta, datetime
import pymysql
from pymysql.cursors import DictCursor

from .users import add_user_msql
from .orders import add_order_msql
from .cb_orders import add_cb_order_msql
from .used_promo import add_used_promo

connect_data = {'host': '45.67.56.166',
                'user': 'infinity_bot',
                'password': 'uG2BjHuZ',
                'db': 'infinity_db',
                'charset': 'utf8mb4'}


def connect():
    conn = pymysql.connect(host=connect_data['host'],
                           user=connect_data['user'],
                           password=connect_data['password'],
                           db=connect_data['db'],
                           charset=connect_data['charset'])
    return conn


# инфо о пользователях
def get_user_data():
    conn = connect()
    cur = conn.cursor(DictCursor)
    cur.execute('select * from bot_manager_users')
    result = cur.fetchall()
    cur.close()
    return result


def get_orders_data():
    conn = connect()
    cur = conn.cursor(DictCursor)
    cur.execute('select * from bot_manager_orders')
    result = cur.fetchall()
    cur.close()
    return result


def get_cb_orders_data():
    conn = connect()
    cur = conn.cursor(DictCursor)
    cur.execute('select * from bot_manager_cashback_orders')
    result = cur.fetchall()
    cur.close()
    return result


# поиск среди проверенных кошельков
def get_used_promo_data():
    # return True
    conn = connect()
    cur = conn.cursor(DictCursor)
    cur.execute('select * from bot_manager_used_promo')
    result = cur.fetchall()
    cur.close()
    return result


# {'id': 66, 'user_id': '5559591475', 'first_name': 'Ванёк', 'last_name': None, 'username': 'Garmonya1904',
# 'first_visit': datetime.datetime(2023, 6, 16, 7, 6, 57, 48902), 'referrer': None,
# 'balance': 0, 'custom_refferal_lvl_id': None, 'ban': 0}
async def move_users():
    print('move_users')

    users = get_user_data()
    for user in users:
        try:
            await add_user_msql(
                user_id=int(user['user_id']),
                full_name=f"{user['first_name']} {user['last_name']}".replace('None', '').strip(),
                username=user['username'],
                first_visit=user['first_visit'],
                referrer=int(user['referrer']) if user['referrer'] else None,
                referral_points=user['balance'],
                custom_referral_lvl_id=user['custom_refferal_lvl_id'],
                ban=bool(int(user['ban'])),
            )
        except Exception as ex:
            print(ex)
            print(user)


'''
{'id': 24665, 'time': datetime.datetime(2024, 10, 3, 18, 17, 53, 449823), 'status': 'successful', 
'user_id': '6934079916', 'coin': 'BTC', 'pay_method': 'С карты на карту', 'coin_sum': 0.00044301, 
'wallet': '1NJmczJXUMGPabHbgZZgp89UwLvYjqNkFy', 'promo': None, 'promo_rate': None, 'exchange_rate': 6433333.0, 
'percent': 12.5, 'amount': 3000.0, 'used_points': None, 'total_amount': 3000.0, 'message_chat_id': '6934079916', 
'message_message_id': '659847', 
'hash': 'https://mempool.space/tx/53ebed2faa2c0190e17efa76e4d2fad0985cdddeaa380b1a297185882f1e6742', 
'commission': 150, 'cashback': None, 'profit': 305.16493880999997, 'referrer': None, 'user_key_id': '0', 
'promo_used_id': None, 'name_user': 'Ра'}
'''
async def move_orders():
    orders = get_orders_data()
    print('move_orders')

    for order in orders:
        try:
            await add_order_msql(
                created_at=order['time'],
                status=order['status'],
                user_id=int(order['user_id']),
                coin=order['coin'],
                pay_method=order['pay_method'],
                coin_sum=order['coin_sum'],
                wallet=order['wallet'],
                promo=order['promo'],
                promo_rate=order['promo_rate'],
                percent=order['percent'],
                amount=int(round(order['amount'])),
                exchange_rate=int(round(order['exchange_rate'])),
                used_points=order['used_points'],
                total_amount=int(round(order['total_amount'])),
                hash=order['hash'],
                commission=order['commission'],
                used_cashback=order['cashback'],
                profit=order['profit'],
                referrer=order['referrer'],
                promo_used_id=order['promo_used_id'],
            )
        except Exception as ex:
            print(ex)
            print(order)


'''
{'id': 59, 'time': datetime.datetime(2024, 10, 1, 5, 4, 6, 95839), 'status': 'successful', 'user_id': '6076270811', 
'name_user': 'SORI MANI❤️', 'username': 'MissManiKriss92', 'card': 'Озон 89049355980 Ирина.б', 'sum': 505, 
'chat_id': '6076270811', 'message_id': '646613'}
'''
async def move_cb_orders():
    orders = get_cb_orders_data()
    print('move_cb_orders')

    for order in orders:
        try:
            await add_cb_order_msql(
                created_at=order['time'],
                status=order['status'],
                user_id=int(order['user_id']),
                wallet=order['card'],
                points=order['sum'],
            )
        except Exception as ex:
            print(ex)
            print(order)

'''
{'id': 10457, 'user_id': '5821087520', 'check_time': datetime.datetime(2024, 10, 3, 19, 35, 34, 537088), 
'coin_code': 'LTC', 'wallet': 'ltc1qyex07vnm6cupysap5y9gt48fyn868uh0tg5t9d'}
'''
async def move_promo():
    promos = get_used_promo_data()
    print('promo')
    for promo in promos:
        try:
            await add_used_promo(
                user_id=int(promo['user_id']),
                promo=promo['promo'],
                rate=0
            )
        except Exception as ex:
            print(ex)
            print(promo)


async def update_db():
    time_start = datetime.now()
    print('start')

    await move_users()
    await move_orders()
    await move_cb_orders()
    await move_promo()

    print(f'time: {datetime.now() - time_start}')
