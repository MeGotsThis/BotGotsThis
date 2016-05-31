# Import some necessary libraries.
from . import config, globals, utils
from .channel import Channel
from .data.socket import Socket
from .thread.background import BackgroundTasker
from .thread.join import JoinThread
from .thread.message import MessageQueue
from .thread.socket import SocketsThread
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

def main(argv):
    print('{time} Starting'.format(time=datetime.datetime.utcnow()))
    globals.messaging = MessageQueue(name='Message Queue')
    globals.sockets = SocketsThread(name='Message Queue')

    globals.clusters['aws'] = Socket(
        'AWS Chat', config.awsServer, config.awsPort)
    globals.sockets.register(globals.clusters['aws'])

    globals.join = JoinThread(name='Join Thread')
    globals.groupChannel = Channel('jtv', globals.clusters['aws'],
                                   float('-inf'))

    globals.background = BackgroundTasker(name='Background Tasker')

    # Start the Threads
    globals.sockets.start()
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
            for channel in db.getAutoJoinsChats():
                utils.joinChannel(channel.broadcaster, channel.priority,
                                  channel.cluster)
    
        globals.messaging.join()
        return 0
    except:
        utils.logException()
        raise
    finally:
        print('{time} Ended'.format(time=datetime.datetime.utcnow()))
