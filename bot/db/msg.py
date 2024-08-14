from datetime import datetime
import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config


class MsgRow(t.Protocol):
    id: int
    key: str
    text: str
    photo_path: str
    photo_id: str
    updated_at: datetime


MsgTable: sa.Table = sa.Table(
    "messages",
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('updated_at', sa.DateTime()),
    sa.Column('key', sa.String(255), unique=True),
    sa.Column('comment', sa.String(255)),
    sa.Column('text', sa.Text),
    sa.Column('photo_id', sa.String(255)),
    sa.Column('photo_path', sa.String(255)),
)


# возвращает текст и фото
async def get_msg(key: str) -> MsgRow:
    query = MsgTable.select().where(MsgTable.c.key == key)
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.first()


# обновляет данные сообщения
async def update_msg(entry_id: int, photo_id: str = None) -> None:
    query = MsgTable.update().where(MsgTable.c.id == entry_id)

    if photo_id:
        query = query.values(photo_id=photo_id)

    async with begin_connection() as conn:
        await conn.execute(query)
