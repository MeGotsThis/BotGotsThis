import bot

import aioodbc  # noqa: F401

from enum import Enum
from typing import cast, Dict, Type  # noqa: F401

from ._base import Database
from .main import DatabaseMain
from .main import AutoJoinChannel, AutoRepeatList, AutoRepeatMessage  # noqa: F401,E501
from .main import RepeatData  # noqa: F401,E501
from .main import CommandProperty, CommandReturn  # noqa: F401
from .oauth import DatabaseOAuth
from .timeout import DatabaseTimeout
from .timezone import DatabaseTimeZone


class Schema(Enum):
    Main = 'main'
    OAuth = 'oauth'
    Timeout = 'timeout'
    TimeZone = 'timezone'


def get_database(schema: Schema=Schema.Main) -> Database:
    databases: Dict[Schema, Type[Database]] = {
        Schema.Main: DatabaseMain,
        Schema.OAuth: DatabaseOAuth,
        Schema.Timeout: DatabaseTimeout,
        Schema.TimeZone: DatabaseTimeZone,
    }
    if schema in databases and schema.value in bot.config.database:
        connectionPool: aioodbc.Pool
        connectionPool = bot.globals.connectionPools[schema.value]
        return databases[schema](connectionPool)
    raise ValueError()


def get_main_database() -> DatabaseMain:
    db: Database = get_database(Schema.Main)
    return cast(DatabaseMain, db)
