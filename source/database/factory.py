from .databasebase import DatabaseBase, DatabaseNone
from .sqlite.sqlite import SQLiteDatabase
import configparser
import os.path

engines = {
    'sqlite': SQLiteDatabase,
    }


def getDatabase() -> DatabaseBase:
    if os.path.isfile('config.ini'):
        ini = configparser.ConfigParser()
        ini.read('config.ini')
        if ini['DATABASE']['engine'] in engines:
            return engines[ini['DATABASE']['engine']](ini['DATABASE'])
    return DatabaseNone()
