from datetime import datetime
import typing as t
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_postgresql

from .base import METADATA, begin_connection
from config import Config


class WalletRow(t.Protocol):
    id: int
    created_at: datetime
    user_id: int
    coin_code: str
    wallet: str


WalletTable: sa.Table = sa.Table(
    "checked_wallets",
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('created_at', sa.DateTime),
    sa.Column('user_id', sa.BigInteger),
    sa.Column('coin_code', sa.String(255)),
    sa.Column('wallet', sa.Boolean),

)


# добавляет кошелёк
async def add_wallet(user_id: int, code: str, wallet: str) -> None:
    query = WalletTable.insert().values(
        user_id=user_id,
        coin_code=code,
        wallet=wallet,
    )

    async with begin_connection() as conn:
        await conn.execute(query)


# возвращает кошелёк
async def get_wallet(code: str, wallet: str) -> WalletRow:
    query = WalletTable.select().where(WalletTable.c.coin_code == code, WalletTable.c.wallet == wallet)
    async with begin_connection() as conn:
        result = await conn.execute(query)

    return result.first()





'''
	`id` INT(10) NOT NULL AUTO_INCREMENT,
	`user_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`check_time` DATETIME(6) NULL DEFAULT NULL,
	`coin_code` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`wallet` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
'''