from datetime import datetime, timedelta
import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config
from enums import OrderStatus


class OrderCBRow(t.Protocol):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    status: str
    coin: str
    wallet: str
    sum: int
    sum_coin: float
    points: int
    cashback: int
    message_id: int
    row: int


OrderCBTable: sa.Table = sa.Table(
    "cashback_orders",
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('created_at', sa.DateTime()),
    sa.Column('updated_at', sa.DateTime()),
    sa.Column('user_id', sa.BigInteger),
    sa.Column('status', sa.String(255), default=OrderStatus.NEW.value),
    sa.Column('coin', sa.String(255)),
    sa.Column('wallet', sa.String(255)),
    sa.Column('sum', sa.Integer),
    sa.Column('sum_coin', sa.Float),
    sa.Column('points', sa.Integer),
    sa.Column('cashback', sa.Integer),
    sa.Column('message_id', sa.Integer),
    sa.Column('row', sa.Integer),
)


# добавляет заказ
async def add_cb_order(
        user_id: int,
        coin: str,
        wallet: str,
        balance: int,
        sum_coin: float,
        points: int,
        cashback: int,
        message_id: int
) -> int:
    now = datetime.now()
    query = OrderCBTable.insert().values(
        created_at=now,
        updated_at=now,
        user_id=user_id,
        coin=coin,
        wallet=wallet,
        sum=balance,
        sum_coin=sum_coin,
        points=points,
        cashback=cashback,
        message_id=message_id,
    )
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.inserted_primary_key[0]


# добавляет заказ
async def add_cb_order_msql(
        created_at: datetime,
        user_id: int,
        wallet: str,
        cashback: int,
        status: str,
) -> int:
    query = OrderCBTable.insert().values(
        created_at=created_at,
        updated_at=created_at,
        user_id=user_id,
        wallet=wallet,
        cashback=cashback,
        status=status,
    )
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.inserted_primary_key[0]


# возвращает заказы на кешбэк
async def get_cb_orders(
        user_id: int = None,
        for_done: bool = False,
        check: bool = False,
        old_orders: bool = False,
        amount: float = None
) -> tuple[OrderCBRow]:
    query = OrderCBTable.select()

    if user_id:
        query = query.where(OrderCBTable.c.user_id == user_id)

    if check:
        query = query.where(sa.or_(
            OrderCBTable.c.status == OrderStatus.NOT_CONF.value,
            OrderCBTable.c.status == OrderStatus.NEW.value
        ))

    if for_done:
        query = query.where(sa.or_(
            OrderCBTable.c.status == OrderStatus.PROC.value,
            OrderCBTable.c.status == OrderStatus.CANCEL.value
        ))

    if old_orders:
        thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
        query = query.where(sa.and_(
            OrderCBTable.c.status == OrderStatus.CANCEL.value,
            OrderCBTable.c.created_at < thirty_minutes_ago
        ))
    if amount:
        query = query.where(OrderCBTable.c.amount == amount)

    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.all()


# возвращает заявку
async def get_cb_order(order_id: int) -> OrderCBRow:
    query = OrderCBTable.select().where(OrderCBTable.c.id == order_id)

    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.first()


# обновляет заявку
async def update_cb_orders(order_id: int, status: str = None, row: int = None) -> None:
    now = datetime.now()
    query = OrderCBTable.update().where(OrderCBTable.c.id == order_id).values(updated_at=now)

    if status:
        query = query.values(status=status)

    if row:
        query = query.values(row=row)

    async with begin_connection() as conn:
        await conn.execute(query)

'''
CREATE TABLE `bot_manager_cashback_orders` (
`id` INT(10) NOT NULL AUTO_INCREMENT,
`time` DATETIME(6) NULL DEFAULT NULL,
`status` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`user_id` VARCHAR(100) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`name_user` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`username` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`card` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`sum` INT(10) NULL DEFAULT NULL,
`chat_id` CHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`message_id` CHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
PRIMARY KEY (`id`) USING BTREE
'''