from datetime import datetime
from random import choice

import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config


class LastMsgRow(t.Protocol):
    user_id: int
    last_sent: datetime


LastMsgTable: sa.Table = sa.Table(
    "antispam_last_msg",
    METADATA,

    sa.Column('user_id', sa.BigInteger, primary_key=True),
    sa.Column('last_sent', sa.DateTime(timezone=True))
)


# Добавляет пользователя
async def update_last_msg(user_id: int) -> None:
    now = datetime.now(Config.tz)

    query = (
        sa_postgresql.insert(LastMsgTable)
        .values(
            user_id=user_id,
            last_sent=now,
        )
        .on_conflict_do_update(
            index_elements=[LastMsgTable.c.user_id],
            set_={'last_sent': now}
        )
    )
    async with begin_connection() as conn:
        await conn.execute(query)


async def get_last_msg(user_id: int) -> LastMsgRow:
    query = LastMsgTable.select().where(LastMsgTable.c.user_id == user_id)

    async with begin_connection() as conn:
        result = await conn.execute(query)
    return result.first()
