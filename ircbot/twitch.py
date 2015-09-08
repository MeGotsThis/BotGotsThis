# Import some necessary libraries.
from config import config
import autoloadbot
import autoloadprivate
import database.factory
import datetime
import ircbot.irc
import importlib
import pkgutil
import sys
import threading
import time
import traceback

print(str(datetime.datetime.utcnow()) + ' Starting')
ircbot.irc.mainChat.start()
ircbot.irc.eventChat.start()
ircbot.irc.groupChat.start()
ircbot.irc.messaging.start()
ircbot.irc.background.start()
ircbot.irc.join.start()

_modulesList = [
    pkgutil.walk_packages(path=autoloadbot.__path__,
                          prefix=autoloadbot.__name__+'.'),
    pkgutil.walk_packages(path=autoloadprivate.__path__,
                                 prefix=autoloadprivate.__name__+'.')
    ]
for _modules in _modulesList:
    for importer, modname, ispkg in _modules:
          __import__(modname)

try:
    ircbot.irc.joinChannel(config.botnick, float('-inf'), ircbot.irc.mainChat)
    if config.owner:
        ircbot.irc.joinChannel(config.owner, float('-inf'),
                               ircbot.irc.mainChat)
    with database.factory.getDatabase() as db:
        for channelRow in db.getAutoJoinsChats():
            params = channelRow['broadcaster'], channelRow['priority'],
            if channelRow['eventServer']:
                params += ircbot.irc.eventChat,
            else:
                params += ircbot.irc.mainChat,
            ircbot.irc.joinChannel(*params)
    
    ircbot.irc.messaging.join()
except:
    ircbot.irc.logException()
    raise
finally:
    print(str(datetime.datetime.utcnow()) + ' Ended')
