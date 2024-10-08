from datetime import datetime, date
import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config


class PromoRow(t.Protocol):
    id: int
    created_at: datetime
    updated_at: datetime
    # user_id: int
    rate: int
    promo: str
    is_active: bool


PromoTable: sa.Table = sa.Table(
    "promo",
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('created_at', sa.DateTime),
    sa.Column('updated_at', sa.DateTime),
    # sa.Column('user_id', sa.BigInteger),
    sa.Column('rate', sa.Integer),
    sa.Column('promo', sa.String(255)),
    sa.Column('is_active', sa.Boolean, default=True),

)


# возвращает промокод
async def get_promo(promo: str = None, promo_id: int = None, is_active: bool = True) -> PromoRow:
    query = PromoTable.select().where(PromoTable.c.is_active == is_active)

    if promo:
        query = query.where(PromoTable.c.promo == promo)

    if promo_id:
        query = query.where(PromoTable.c.id == promo_id)

    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.first()


# возвращает кошелёк
async def update_promo(promo_id: int, user_id: int = None, used: bool = None) -> None:
    query = PromoTable.update().where(PromoTable.c.id == promo_id)

    if used is not None:
        query = query.values(is_used=used)

    if user_id is not None:
        query = query.values(user_id=user_id)

    async with begin_connection() as conn:
        await conn.execute(query)

