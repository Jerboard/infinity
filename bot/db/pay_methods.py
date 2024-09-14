from datetime import datetime
import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config


class PayMethodRow(t.Protocol):
    id: int
    name: str
    card: str
    is_active: bool


PayMethodTable: sa.Table = sa.Table(
    "pay_methods",
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('name', sa.String(255)),
    sa.Column('card', sa.String(255)),
    sa.Column('is_active', sa.Boolean),

)


# возвращает метод оплаты по id
async def get_pay_method() -> PayMethodRow:
    query = PayMethodTable.select().where(PayMethodTable.c.is_active == True)

    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.first()


# возвращает список методов оплаты
async def get_all_pay_method(only_active: bool = True) -> tuple[PayMethodRow]:
    query = PayMethodTable.select()

    if only_active:
        query = query.where(PayMethodTable.c.is_active)
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.all()


"""
	`id` INT(10) NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`card` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`is_active` TINYINT(1) NOT NULL,
"""