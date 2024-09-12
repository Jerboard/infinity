from datetime import datetime, timedelta
import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config
from enums import OrderStatus


class OrderRow(t.Protocol):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    status: str
    coin: str
    pay_method: str
    coin_sum: float
    wallet: str
    promo: str
    promo_rate: int
    exchange_rate: int
    percent: float
    amount: int
    total_amount: int
    used_points: int
    message_id: int
    hash: str
    commission: int
    cashback: int
    profit: float
    referrer: int
    user_key_id: str
    promo_used_id: int


OrderTable: sa.Table = sa.Table(
    "orders",
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('created_at', sa.DateTime()),
    sa.Column('updated_at', sa.DateTime()),
    sa.Column('user_id', sa.BigInteger),
    sa.Column('status', sa.String(255)),
    sa.Column('coin', sa.String(255)),
    sa.Column('pay_method', sa.String(255)),
    sa.Column('coin_sum', sa.Float()),
    sa.Column('wallet', sa.String(255)),
    sa.Column('promo', sa.String(255)),
    sa.Column('promo_rate', sa.Integer),
    sa.Column('exchange_rate', sa.Integer),
    sa.Column('percent', sa.Float()),
    sa.Column('amount', sa.Integer),
    sa.Column('total_amount', sa.Integer),
    sa.Column('used_points', sa.Integer, default=0),
    sa.Column('message_id', sa.Integer),
    sa.Column('hash', sa.String(255)),
    sa.Column('commission', sa.Integer),
    sa.Column('cashback', sa.Integer),
    sa.Column('profit', sa.Float()),
    sa.Column('referrer', sa.BigInteger),
    sa.Column('user_key_id', sa.Integer),
    sa.Column('promo_used_id', sa.Integer),
)


# добавляет заказ
async def add_order(
        user_id: int,
        coin: str,
        pay_method: str,
        coin_sum: float,
        wallet: str,
        promo: str,
        promo_rate: int,
        exchange_rate: str,
        percent: float,
        amount: int,
        used_points: int,
        total_amount: int,
        message_id: int,
        promo_used_id: int,
        commission: int,
) -> int:
    now = datetime.now()
    query = OrderTable.insert().values(
        created_at=now,
        updated_at=now,
        status=OrderStatus.NOT_CONF.value,
        user_id=user_id,
        coin=coin,
        pay_method=pay_method,
        coin_sum=coin_sum,
        wallet=wallet,
        promo=promo,
        promo_rate=promo_rate,
        exchange_rate=exchange_rate,
        percent=percent,
        amount=amount,
        used_points=used_points,
        total_amount=total_amount,
        message_id=message_id,
        promo_used_id=promo_used_id,
        commission=commission,
    )
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.inserted_primary_key[0]


# возвращает заказы
async def get_orders(
        user_id: int = None,
        for_done: bool = False,
        check: bool = False,
        old_orders: bool = False,
        amount: float = None
) -> tuple[OrderRow]:
    query = OrderTable.select()

    if user_id:
        query = query.where(OrderTable.c.user_id == user_id)

    if check:
        query = query.where(sa.or_(
            OrderTable.c.status == OrderStatus.NOT_CONF.value,
            OrderTable.c.status == OrderStatus.NEW.value
        ))

    if for_done:
        query = query.where(sa.or_(
            OrderTable.c.status == OrderStatus.PROC.value,
            OrderTable.c.status == OrderStatus.CANCEL.value
        ))

    if old_orders:
        thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
        query = query.where(sa.and_(
            OrderTable.c.status == OrderStatus.CANCEL.value,
            OrderTable.c.created_at < thirty_minutes_ago
        ))
    if amount:
        query = query.where(OrderTable.c.amount == amount)

    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.all()


# обновляет заявку
async def update_orders(order_id: int, status: str = None) -> None:
    query = OrderTable.update().where(OrderTable.c.id == order_id)

    if status:
        query = query.values(status=status)

    async with begin_connection() as conn:
        await conn.execute(query)


"""
`id` INT(10) NOT NULL AUTO_INCREMENT,
`time` DATETIME(6) NULL DEFAULT NULL,
`status` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`user_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`coin` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`pay_method` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`coin_sum` FLOAT NULL DEFAULT NULL,
`wallet` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`promo` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`promo_rate` DOUBLE NULL DEFAULT NULL,
`exchange_rate` DOUBLE NULL DEFAULT NULL,
`percent` DOUBLE NULL DEFAULT NULL,
`amount` DOUBLE NULL DEFAULT NULL,
`used_points` INT(10) NULL DEFAULT '0',
`total_amount` DOUBLE NULL DEFAULT NULL,
`message_chat_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`message_message_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`hash` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`commission` INT(10) NULL DEFAULT NULL,
`cashback` DOUBLE NULL DEFAULT NULL,
`profit` DOUBLE NULL DEFAULT NULL,
`referrer` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`user_key_id` VARCHAR(50) NOT NULL DEFAULT '0' COLLATE 'utf8mb4_0900_ai_ci',
`promo_used_id` INT(10) NULL DEFAULT NULL,
`name_user` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
"""
