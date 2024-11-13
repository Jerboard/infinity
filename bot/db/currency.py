from datetime import datetime
import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config


class CurrencyRow(t.Protocol):
    id: int
    updated_at: datetime
    created_at: datetime
    name: str
    code: str
    rate: float
    ratio: float
    min: float
    max: float
    commission: float
    buy_price: float
    is_active: bool
    round: int


CurrencyTable: sa.Table = sa.Table(
    "currency",
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('created_at', sa.DateTime()),
    sa.Column('updated_at', sa.DateTime()),
    sa.Column('name', sa.String(255)),
    sa.Column('code', sa.String(255), unique=True),
    sa.Column('rate', sa.Float()),
    sa.Column('ratio', sa.Float()),
    sa.Column('min', sa.Float()),
    sa.Column('max', sa.Float()),
    sa.Column('commission', sa.Float()),
    sa.Column('buy_price', sa.Float()),
    sa.Column('is_active', sa.Boolean),
    sa.Column('round', sa.Integer),
)


# возвращает валюту по id
async def get_currency(currency_id: int = None, currency_code: str = None) -> CurrencyRow:
    query = CurrencyTable.select()

    if currency_id:
        query = query.where(CurrencyTable.c.id == currency_id)
    if currency_code:
        query = query.where(CurrencyTable.c.code == currency_code)

    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.first()


# возвращает список валют
async def get_all_currency(only_active: bool = True) -> tuple[CurrencyRow]:
    query = CurrencyTable.select()

    if only_active:
        query = query.where(CurrencyTable.c.is_active)
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.all()


# обновляет курс
async def update_currency(currency_code: str, rate: float) -> None:
    now = datetime.now()
    query = CurrencyTable.update().where(CurrencyTable.c.code == currency_code).values(rate=rate, updated_at=now)

    async with begin_connection() as conn:
        await conn.execute(query)



"""
	`id` INT(10) NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`code` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`rate` DOUBLE NULL DEFAULT NULL,
	`ratio` DOUBLE NULL DEFAULT NULL,
	`min` DOUBLE NULL DEFAULT NULL,
	`max` DOUBLE NULL DEFAULT NULL,
	`commission` DOUBLE NULL DEFAULT NULL,
	`buy_price` DOUBLE NULL DEFAULT NULL,
	`is_active` TINYINT(1) NOT NULL,
	`round` INT(10) NULL DEFAULT NULL,
"""