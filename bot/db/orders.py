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
    pay_method_id: int
    pay_method: str
    card: str
    coin_sum: float
    wallet: str
    promo: str
    promo_rate: int
    exchange_rate: int
    percent: float
    amount: int
    total_amount: int
    used_points: int
    used_cashback: int
    message_id: int
    hash: str
    commission: int
    cashback: int
    profit: float
    referrer: int
    promo_used_id: int
    user_key_id: str
    referrer_id: int
    add_ref_points: int
    add_cashback: int
    row: int
    request_id: int


OrderTable: sa.Table = sa.Table(
    "orders",
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('created_at', sa.DateTime()),
    sa.Column('updated_at', sa.DateTime()),
    sa.Column('user_id', sa.BigInteger),
    sa.Column('status', sa.String(255)),
    sa.Column('coin', sa.String(255)),
    sa.Column('pay_method_id', sa.Integer),
    sa.Column('pay_method', sa.String(255)),
    sa.Column('card', sa.String(255)),
    sa.Column('coin_sum', sa.Float()),
    sa.Column('wallet', sa.String(255)),
    sa.Column('promo', sa.String(255)),
    sa.Column('promo_rate', sa.Integer),
    sa.Column('exchange_rate', sa.Integer),
    sa.Column('percent', sa.Float()),
    sa.Column('amount', sa.Integer),
    sa.Column('total_amount', sa.Integer),
    sa.Column('used_points', sa.Integer, default=0),
    sa.Column('used_cashback', sa.Integer, default=0),
    sa.Column('message_id', sa.Integer),
    sa.Column('hash', sa.String(255)),
    sa.Column('commission', sa.Integer),
    sa.Column('cashback', sa.Integer),
    sa.Column('profit', sa.Float(), default=0),
    sa.Column('referrer', sa.BigInteger),
    # sa.Column('user_key_id', sa.Integer),
    sa.Column('promo_used_id', sa.Integer),
    sa.Column('add_ref_points', sa.Integer, default=0),
    sa.Column('add_cashback', sa.Integer, default=0),
    sa.Column('row', sa.Integer),
    sa.Column('request_id', sa.Integer, default=0),
)


# добавляет заказ
async def add_order(
        user_id: int,
        coin: str,
        pay_method_id: int,
        pay_method: str,
        card: str,
        coin_sum: float,
        wallet: str,
        promo: str,
        promo_rate: int,
        exchange_rate: str,
        percent: float,
        amount: int,
        used_points: int,
        used_cashback: int,
        total_amount: int,
        # message_id: int,
        promo_used_id: int,
        commission: int,
        profit: int,
        cashback: int,
        request_id: int
) -> int:
    now = datetime.now()
    query = OrderTable.insert().values(
        created_at=now,
        updated_at=now,
        status=OrderStatus.NOT_CONF.value,
        user_id=user_id,
        coin=coin,
        pay_method_id=pay_method_id,
        pay_method=pay_method,
        card=card,
        coin_sum=coin_sum,
        wallet=wallet,
        promo=promo,
        promo_rate=promo_rate,
        exchange_rate=exchange_rate,
        percent=percent,
        amount=amount,
        used_points=used_points,
        used_cashback=used_cashback,
        total_amount=total_amount,
        # message_id=message_id,
        promo_used_id=promo_used_id,
        commission=commission,
        profit=profit,
        cashback=cashback,
        request_id=request_id,
    )
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.inserted_primary_key[0]


# возвращает заказы
async def get_orders(
        user_id: int = None,
        status: str = None,
        for_done: bool = False,
        check: bool = False,
        old_orders: bool = False,
        amount: float = None,
        referrer_id: int = None,
        desc_order: bool = False
) -> tuple[OrderRow]:
    query = OrderTable.select()

    if user_id:
        query = query.where(OrderTable.c.user_id == user_id)

    if status:
        query = query.where(OrderTable.c.status == status)

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
        thirty_minutes_ago = datetime.now() - timedelta(minutes=Config.order_live_time)

        query = query.where(
            sa.or_(
                OrderTable.c.status == OrderStatus.CANCEL.value,
                sa.and_(
                    OrderTable.c.status == OrderStatus.NOT_CONF.value, OrderTable.c.created_at < thirty_minutes_ago
                )
            )
        )
    if amount:
        query = query.where(OrderTable.c.amount == amount)

    if referrer_id:
        query = query.where(OrderTable.c.referrer == referrer_id)

    if desc_order:
        query = query.order_by(sa.desc(OrderTable.c.created_at))

    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.all()


# возвращает заявку
async def get_order(order_id: int) -> OrderRow:
    query = OrderTable.select().where(OrderTable.c.id == order_id)

    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.first()


# обновляет заявку
async def update_order(
        order_id: int,
        profit: float = None,
        status: int = None,
        add_ref_points: int = None,
        add_cashback: int = None,
        row: int = None,
        message_id: int = None,
) -> None:
    query = OrderTable.update().where(OrderTable.c.id == order_id).values(updated_at=datetime.now())

    if status:
        query = query.values(status=status)

    if profit:
        query = query.values(profit=profit)

    if add_ref_points:
        query = query.values(add_ref_points=add_ref_points)

    if add_cashback:
        query = query.values(add_cashback=add_cashback)

    if row:
        query = query.values(row=row)

    if message_id:
        query = query.values(message_id=message_id)

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
