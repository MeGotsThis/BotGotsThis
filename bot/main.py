# Import some necessary libraries.
from . import config
from . import globals
from . import utils
from source.database.factory import getDatabase
import source.private.autoload as privateAuto
import source.public.autoload as publicAuto
import datetime
import importlib
import pkgutil
import sys
import threading
import time
import traceback

print(str(datetime.datetime.utcnow()) + ' Starting')
globals.mainChat.start()
globals.eventChat.start()
globals.groupChat.start()
globals.messaging.start()
globals.background.start()
globals.join.start()

_modulesList = [
    pkgutil.walk_packages(path=publicAuto.__path__,
                          prefix=publicAuto.__name__+'.'),
    pkgutil.walk_packages(path=privateAuto.__path__,
                          prefix=privateAuto.__name__+'.')
    ]
for _modules in _modulesList:
    for importer, modname, ispkg in _modules:
          importlib.import_module(modname)

try:
    globals.joinChannel(config.botnick, float('-inf'), globals.mainChat)
    if config.owner:
        globals.joinChannel(config.owner, float('-inf'), globals.mainChat)
    with getDatabase() as db:
        for channelRow in db.getAutoJoinsChats():
            params = channelRow['broadcaster'], channelRow['priority'],
            if channelRow['eventServer']:
                params += globals.eventChat,
            else:
                params += globals.mainChat,
            utils.joinChannel(*params)
    
    globals.messaging.join()
except:
    globals.logException()
    raise
finally:
    print(str(datetime.datetime.utcnow()) + ' Ended')
