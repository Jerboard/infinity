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


'''
	`id` INT(10) NOT NULL AUTO_INCREMENT,
	`count_users` INT(10) NULL DEFAULT NULL,
	`percent` DOUBLE NULL DEFAULT NULL,
'''