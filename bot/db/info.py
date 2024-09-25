from datetime import datetime, date
import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config


class InfoRow(t.Protocol):
    id: int
    update_at: datetime
    cashback: int


InfoTable: sa.Table = sa.Table(
    "info",
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('update_at', sa.DateTime),
    sa.Column('cashback', sa.Integer),


)


# возвращает кошелёк
async def get_info() -> InfoRow:
    query = InfoTable.select().where(InfoTable.c.id == 1)
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.first()