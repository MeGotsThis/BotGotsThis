import configparser
import database.database
import database.sqlite.sqlite

engines = {
    'sqlite': database.sqlite.sqlite.SQLiteDatabase,
    }

def getDatabase():
    ini = configparser.ConfigParser()
    ini.read('config.ini')
    if ini['DATABASE']['engine'] in engines:
        return engines[ini['DATABASE']['engine']](ini['DATABASE'])
    return database.database.DatabaseBase()
