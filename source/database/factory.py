import configparser
import database.databasebase
import database.sqlite.sqlite
import os.path

engines = {
    'sqlite': database.sqlite.sqlite.SQLiteDatabase,
    }

def getDatabase():
    if os.path.isfile('config.ini'):
        ini = configparser.ConfigParser()
        ini.read('config.ini')
        if ini['DATABASE']['engine'] in engines:
            return engines[ini['DATABASE']['engine']](ini['DATABASE'])
    return database.databasebase.DatabaseBase()
