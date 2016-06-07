# Import some necessary libraries.
import datetime
import importlib
import pkgutil
import source.private.autoload as privateAuto
import source.public.autoload as publicAuto
from itertools import chain
from importlib.abc import PathEntryFinder
from source.database.factory import getDatabase
from typing import Generator, List, Iterable, Optional, Tuple
from . import config, globals, utils
from .data.channel import Channel
from .data.socket import Socket
from .thread.background import BackgroundTasker
from .thread.join import JoinThread
from .thread.socket import SocketsThread


def main(argv:Optional[List[str]]=None) -> int:
    print('{time} Starting'.format(time=datetime.datetime.utcnow()))
    globals.running = True
    globals.sockets = SocketsThread(name='Sockets Thread')

    globals.clusters['aws'] = Socket(
        'AWS Chat', config.awsServer, config.awsPort)
    globals.sockets.register(globals.clusters['aws'])

    globals.join = JoinThread(name='Join Thread')
    globals.groupChannel = Channel('jtv', globals.clusters['aws'],
                                   float('-inf'))

    globals.background = BackgroundTasker(name='Background Tasker')

    # Start the Threads
    globals.sockets.start()
    globals.background.start()
    globals.join.start()

    _modulesList = [
        pkgutil.walk_packages(path=publicAuto.__path__,  # type: ignore --
                              prefix=publicAuto.__name__ + '.'),
        pkgutil.walk_packages(path=privateAuto.__path__,  # type: ignore --
                              prefix=privateAuto.__name__ + '.')
        ]  # type: Iterable[Generator[Tuple[PathEntryFinder, str, bool], None, None]]
    for importer, modname, ispkg in chain(*_modulesList):  # --type: PathEntryFinder, str, bool
        importlib.import_module(modname)

    try:
        utils.joinChannel(config.botnick, float('-inf'), 'aws')
        if config.owner:
            utils.joinChannel(config.owner, float('-inf'), 'aws')
        with getDatabase() as db:
            for channel in db.getAutoJoinsChats():
                utils.joinChannel(channel.broadcaster, channel.priority,
                                  channel.cluster)
    
        globals.sockets.join()
        return 0
    except:
        globals.running = False
        utils.logException()
        raise
    finally:
        print('{time} Ended'.format(time=datetime.datetime.utcnow()))
