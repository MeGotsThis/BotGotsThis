# Import some necessary libraries.
from . import config, globals, utils
from .channel import Channel
from .thread.background import BackgroundTasker
from .thread.join import JoinThread
from .thread.message import MessageQueue
from .thread.socket import SocketThread
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
globals.messaging = MessageQueue(name='Message Queue')

globals.clusters['main'] = SocketThread(config.mainServer, config.mainPort,
                                        name='Main Chat')
globals.clusters['event'] = SocketThread(config.eventServer, config.eventPort,
                                         name='Event Chat')
globals.clusters['group'] = SocketThread(config.groupServer, config.groupPort,
                                         name='Group Chat')
globals.clusters['aws'] = SocketThread(config.awsServer, config.awsPort,
                                       name='AWS Chat')

globals.join = JoinThread(name='Join Thread')
globals.groupChannel = Channel(config.botnick, globals.clusters['group'],
                               float('-inf'))

globals.background = BackgroundTasker(name='Background Tasker')

# Start the Threads
for st in globals.clusters.values():
    st.start()
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
    utils.joinChannel(config.botnick, float('-inf'), 'aws')
    if config.owner:
        utils.joinChannel(config.owner, float('-inf'), 'aws')
    with getDatabase() as db:
        for channelRow in db.getAutoJoinsChats():
            params = channelRow['broadcaster'], channelRow['priority'],
            params += channelRow['cluster'],
            utils.joinChannel(*params)
    
    globals.messaging.join()
except:
    utils.logException()
    raise
finally:
    print(str(datetime.datetime.utcnow()) + ' Ended')
