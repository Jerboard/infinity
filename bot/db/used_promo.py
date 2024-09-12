from datetime import datetime, date
import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config


class UsedPromoRow(t.Protocol):
    id: int
    created_at: datetime
    user_id: int
    promo: str


UsedPromoTable: sa.Table = sa.Table(
    "used_promo",
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('created_at', sa.DateTime),
    sa.Column('promo', sa.String(255)),
    sa.Column('user_id', sa.BigInteger)
)


# добавляет использованные промо
async def add_used_promo(promo: str, user_id) -> None:
    now = datetime.now()
    query = UsedPromoTable.insert().values(
        created_at=now,
        promo=promo,
        user_id=user_id
    )
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.inserted_primary_key


# возвращает использованые промо
async def get_used_promo(promo: str, user_id: int) -> tuple[UsedPromoRow]:
    query = UsedPromoTable.select().where(
        UsedPromoTable.c.promo == promo,
        UsedPromoTable.c.user_id == user_id,
    )
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.all()


# удаляет промо
async def del_used_promo(promo: str, user_id: int) -> None:
    query = UsedPromoTable.delete().where(
        UsedPromoTable.c.promo == promo,
        UsedPromoTable.c.user_id == user_id,
    )
    async with begin_connection() as conn:
        await conn.execute(query)


"""
	`id` INT(10) NOT NULL AUTO_INCREMENT,
	`promo` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`user_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`time` DATETIME(6) NULL DEFAULT NULL,
"""