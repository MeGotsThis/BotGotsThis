# Import some necessary libraries.
import asyncio
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
from .thread.join import JoinThread
from .thread.logging import Logging
from .thread.socket import SocketsThread
from .async_task import background

ModuleList = Iterable[Generator[Tuple[PathEntryFinder, str, bool], None, None]]


def main(argv: Optional[List[str]]=None) -> int:
    print('{time} Starting'.format(time=utils.now()))
    bot.globals.running = True
    bot.globals.sockets = SocketsThread(name='Sockets Thread')

    bot.globals.clusters['aws'] = data.Socket(
        'AWS Chat', bot.config.awsServer, bot.config.awsPort)

    bot.globals.join = JoinThread(name='Join Thread')

    bot.globals.logging = Logging()

    # Start the Threads
    bot.globals.logging.start()
    bot.globals.sockets.start()
    bot.globals.join.start()

    _modulesList: ModuleList = [
        pkgutil.walk_packages(path=publicAuto.__path__,  # type: ignore
                              prefix=publicAuto.__name__ + '.'),
        pkgutil.walk_packages(path=privateAuto.__path__,  # type: ignore
                              prefix=privateAuto.__name__ + '.')
        ]
    importer: PathEntryFinder
    modname: str
    ispkg: bool
    for importer, modname, ispkg in chain(*_modulesList):
        importlib.import_module(modname)

    try:
        utils.joinChannel(bot.config.botnick, float('-inf'), 'aws')
        bot.globals.groupChannel = bot.globals.channels[bot.config.botnick]
        if bot.config.owner:
            utils.joinChannel(bot.config.owner, float('-inf'), 'aws')
        with getDatabase() as db:
            autojoin: AutoJoinChannel
            for autoJoin in db.getAutoJoinsChats():
                utils.joinChannel(autoJoin.broadcaster, autoJoin.priority,
                                  autoJoin.cluster)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(background.run_tasks())
        loop.close()
        return 0
    except:
        bot.globals.running = False
        utils.logException()
        raise
    finally:
        while bot.globals.logging.queue.qsize():
            pass
        print('{time} Ended'.format(time=utils.now()))
