from datetime import datetime
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
    custom_refferal_lvl_id: int
    ban: bool


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
    sa.Column('custom_refferal_lvl_id', sa.Integer, default=0),
    sa.Column('ban', sa.Boolean, default=False),
)


# Добавляет пользователя
async def add_user(user_id: int, full_name: str, username: str, referrer: int = None) -> None:
    now = datetime.now(Config.tz)
    query = (
        sa_postgresql.insert(UserTable)
        .values(
            user_id=user_id,
            full_name=full_name,
            username=username,
            first_visit=now,
            last_visit=now,
            referrer=referrer,
        )
        .on_conflict_do_update(
            index_elements=[UserTable.c.user_id],
            set_={"full_name": full_name, 'username': username, 'last_visit': now}
        )
    )
    async with begin_connection() as conn:
        await conn.execute(query)


# возвращает данные пользователя
async def get_user_info(user_id: int) -> UserRow:
    query = UserTable.select().where(UserTable.c.user_id == user_id)
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.first()


# возвращает список пользователей
async def get_users() -> tuple[UserRow]:
    query = UserTable.select()
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.all()


# обновляет данные пользователя
async def update_user_info(user_id: int, add_balance: int = None) -> None:
    query = UserTable.update().where(UserTable.c.user_id == user_id)
    if add_balance:
        query = query.values(balance=UserTable.c.balance + add_balance)
    async with begin_connection() as conn:
        await conn.execute(query)

