from typing import Dict, Type
from . import DatabaseBase
from .databasenone import DatabaseNone
from .sqlite import SQLiteDatabase
import configparser
import os.path

engines: Dict[str, Type[DatabaseBase]] = {
    'sqlite': SQLiteDatabase,
    }


def getDatabase() -> DatabaseBase:
    if os.path.isfile('config.ini'):
        ini: configparser.ConfigParser = configparser.ConfigParser()
        ini.read('config.ini')
        if ini['DATABASE']['engine'] in engines:
            return engines[ini['DATABASE']['engine']](ini['DATABASE'])
    return DatabaseNone({})
