import bot

from enum import Enum
from typing import Dict, Type  # noqa: F401

from ._base import Database
from .main import DatabaseMain
from .main import AutoJoinChannel, AutoRepeatList, AutoRepeatMessage  # noqa: F401, E501
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
        return databases[schema](bot.globals.connectionPools[schema])
    raise ValueError()
