from typing import Dict, Type
from . import DatabaseBase
from .databasenone import DatabaseNone
from .sqlite import SQLiteDatabase
import configparser
import os.path

engines = {
    'sqlite': SQLiteDatabase,
    }  # type: Dict[str, Type[DatabaseBase]]


def getDatabase() -> DatabaseBase:
    if os.path.isfile('config.ini'):
        ini = configparser.ConfigParser()  # type: configparser.ConfigParser
        ini.read('config.ini')
        if ini['DATABASE']['engine'] in engines:
            return engines[ini['DATABASE']['engine']](ini['DATABASE'])
    return DatabaseNone(ini['DATABASE'])
