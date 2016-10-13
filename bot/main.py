# Import some necessary libraries.
import bot.config
import bot.globals
import importlib
import pkgutil
import source.private.autoload as privateAuto
import source.public.autoload as publicAuto
from itertools import chain
from importlib.abc import PathEntryFinder
from source.database import AutoJoinChannel
from source.database.factory import getDatabase
from typing import Generator, List, Iterable, Optional, Tuple
from . import data, utils
from .thread.background import BackgroundTasker
from .thread.join import JoinThread
from .thread.logging import Logging
from .thread.socket import SocketsThread


def main(argv: Optional[List[str]]=None) -> int:
    print('{time} Starting'.format(time=utils.now()))
    bot.globals.running = True
    bot.globals.sockets = SocketsThread(name='Sockets Thread')

    bot.globals.clusters['aws'] = data.Socket(
        'AWS Chat', bot.config.awsServer, bot.config.awsPort)

    bot.globals.join = JoinThread(name='Join Thread')
    bot.globals.groupChannel = data.Channel('jtv', bot.globals.clusters['aws'],
                                            float('-inf'))

    bot.globals.logging = Logging()
    bot.globals.background = BackgroundTasker(name='Background Tasker')

    # Start the Threads
    bot.globals.logging.start()
    bot.globals.sockets.start()
    bot.globals.background.start()
    bot.globals.join.start()

    # TODO: Fix mypy
    _modulesList = [
        pkgutil.walk_packages(path=publicAuto.__path__,  # type: ignore
                              prefix=publicAuto.__name__ + '.'),
        pkgutil.walk_packages(path=privateAuto.__path__,  # type: ignore
                              prefix=privateAuto.__name__ + '.')
        ]  # type: Iterable[Generator[Tuple[PathEntryFinder, str, bool], None, None]]
    for importer, modname, ispkg in chain(*_modulesList):  # type: PathEntryFinder, str, bool
        importlib.import_module(modname)

    try:
        utils.joinChannel(bot.config.botnick, float('-inf'), 'aws')
        if bot.config.owner:
            utils.joinChannel(bot.config.owner, float('-inf'), 'aws')
        with getDatabase() as db:
            for autoJoin in db.getAutoJoinsChats():  # type: AutoJoinChannel
                utils.joinChannel(autoJoin.broadcaster, autoJoin.priority,
                                  autoJoin.cluster)
    
        bot.globals.sockets.join()
        return 0
    except:
        bot.globals.running = False
        utils.logException()
        raise
    finally:
        while bot.globals.logging.queue.qsize():
            pass
        print('{time} Ended'.format(time=utils.now()))
