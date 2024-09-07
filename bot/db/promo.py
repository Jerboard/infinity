from datetime import datetime, date
import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config


class PromoRow(t.Protocol):
    id: int
    created_at: datetime
    start_date: date
    end_date: date
    rate: int
    many: int
    promo: int
    is_active: bool
    is_onetime: bool


PromoTable: sa.Table = sa.Table(
    "promo",
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('created_at', sa.DateTime),
    sa.Column('start_date', sa.Date),
    sa.Column('end_date', sa.Date),
    sa.Column('rate', sa.Integer),
    sa.Column('promo', sa.String(255)),
    sa.Column('many', sa.Integer),
    sa.Column('is_active', sa.Boolean),
    sa.Column('is_onetime', sa.Boolean),

)


# возвращает кошелёк
async def get_promo(promo: str) -> PromoRow:
    today = datetime.now().date()
    query = PromoTable.select().where(
        PromoTable.c.promo == promo,
        PromoTable.c.start_date <= today,
        PromoTable.c.end_date >= today,
    )
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.first()



"""
`id` INT(10) NOT NULL AUTO_INCREMENT,
`promo` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
`rate` INT(10) NULL DEFAULT NULL,
`start_date` DATE NULL DEFAULT NULL,
`end_date` DATE NULL DEFAULT NULL,
`many` INT(10) NOT NULL,
`is_active` TINYINT(1) NOT NULL,
`is_onetime` TINYINT(3) NULL DEFAULT '0',
"""