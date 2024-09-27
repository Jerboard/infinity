from datetime import datetime
import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config


class CBLevelsRow(t.Protocol):
    id: int
    count_users: int
    percent: float


CBLevelsTable: sa.Table = sa.Table(
    "cashback_levels",
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('count_users', sa.Integer),
    sa.Column('percent', sa.Float),
)


# возвращает уровень кешбека
async def get_referral_lvl(lvl_id: int = None, count_user: int = None) -> CBLevelsRow:
    query = CBLevelsTable.select()

    if lvl_id:
        query = query.where(CBLevelsTable.c.id == lvl_id)

    if count_user:
        query = query.where(CBLevelsTable.c.count_users <= count_user).order_by(sa.desc(CBLevelsTable.c.count_users))

    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.first()


'''
	`id` INT(10) NOT NULL AUTO_INCREMENT,
	`count_users` INT(10) NULL DEFAULT NULL,
	`percent` DOUBLE NULL DEFAULT NULL,
'''