from datetime import datetime
from random import choice

import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config


class UserRow(t.Protocol):
    id: int
    user_id: int
    full_name: str
    username: str
    first_visit: datetime
    last_visit: datetime
    referrer: int
    balance: int
    referral_points: int
    cashback: int
    custom_referral_lvl_id: int
    ban: bool
    ref_code: str


UserTable: sa.Table = sa.Table(
    "users",
    METADATA,

    sa.Column('user_id', sa.BigInteger, primary_key=True),
    sa.Column('full_name', sa.String(255)),
    sa.Column('username', sa.String(255)),
    sa.Column('first_visit', sa.DateTime(timezone=True)),
    sa.Column('last_visit', sa.DateTime(timezone=True)),
    sa.Column('referrer', sa.BigInteger),
    sa.Column('balance', sa.Integer, default=0),
    sa.Column('referral_points', sa.Integer, default=0),
    sa.Column('cashback', sa.Integer, default=0),
    sa.Column('custom_referral_lvl_id', sa.Integer, default=None),
    sa.Column('ban', sa.Boolean, default=False),
    sa.Column('ref_code', sa.String(255)),
)


# даёт случайную сроку для реферальной ссылки
def get_ref_code() -> str:
    return ''.join([choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(10)])


# Добавляет пользователя
async def add_user(user_id: int, full_name: str, username: str, referrer: int = None) -> None:
    now = datetime.now()
    query = (
        sa_postgresql.insert(UserTable)
        .values(
            user_id=user_id,
            full_name=full_name,
            username=username,
            first_visit=now,
            last_visit=now,
            referrer=referrer,
            ref_code=get_ref_code()
        )
        .on_conflict_do_update(
            index_elements=[UserTable.c.user_id],
            set_={"full_name": full_name, 'username': username, 'last_visit': now}
        )
    )
    async with begin_connection() as conn:
        await conn.execute(query)


# {'id': 66, 'user_id': '5559591475', 'first_name': 'Ванёк', 'last_name': None, 'username': 'Garmonya1904',
# 'first_visit': datetime.datetime(2023, 6, 16, 7, 6, 57, 48902), 'referrer': None,
# 'balance': 0, 'custom_refferal_lvl_id': None, 'ban': 0}
# Добавляет пользователя из старой базы
async def add_user_msql(
        user_id: int,
        full_name: str,
        username: str,
        first_visit: datetime,
        referrer: int = None,
        referral_points: int = None,
        custom_referral_lvl_id: int = None,
        ban: bool = None,

) -> None:
    now = datetime.now()
    query = (
        sa_postgresql.insert(UserTable)
        .values(
            user_id=user_id,
            full_name=full_name,
            username=username,
            first_visit=first_visit,
            last_visit=now,
            referrer=referrer,
            referral_points=referral_points,
            custom_referral_lvl_id=custom_referral_lvl_id,
            ban=ban,
            ref_code=get_ref_code()
        )
        .on_conflict_do_update(
            index_elements=[UserTable.c.user_id],
            set_={"full_name": full_name, 'username': username, 'last_visit': now}
        )
    )
    async with begin_connection() as conn:
        await conn.execute(query)


# возвращает данные пользователя
async def get_user_info(user_id: int = None, ref_code: str = None) -> UserRow:
    query = UserTable.select()

    if user_id:
        query = query.where(UserTable.c.user_id == user_id)
    if ref_code:
        query = query.where(UserTable.c.ref_code == ref_code)
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.first()


# возвращает список пользователей
async def get_users(referrer: int = None) -> tuple[UserRow]:
    query = UserTable.select().where(UserTable.c.ban == False)
    if referrer:
        query = query.where(UserTable.c.referrer == referrer)
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.all()


# обновляет данные пользователя
async def update_user_info(
        user_id: int,
        add_balance: int = None,
        add_point: int = None,
        add_cashback: int = None
) -> None:
    query = UserTable.update().where(UserTable.c.user_id == user_id)
    if add_balance:
        query = query.values(balance=UserTable.c.balance + add_balance)

    if add_point:
        query = query.values(referral_points=UserTable.c.referral_points + add_point)

    if add_cashback:
        query = query.values(cashback=UserTable.c.cashback + add_cashback)

    async with begin_connection() as conn:
        await conn.execute(query)
