# Import some necessary libraries.
import asyncio
import bot
import bot.globals
import importlib
import pkgutil
import source.private.autoload as privateAuto
import source.public.autoload as publicAuto
from itertools import chain
from importlib.abc import PathEntryFinder
from source import database
from source.database import AutoJoinChannel
from typing import Generator, List, Iterable, Optional, Tuple, cast
from . import data, utils
from .coroutine import background, connection, join, logging

ModuleList = Iterable[Generator[Tuple[PathEntryFinder, str, bool], None, None]]


async def initializer() -> None:
    await bot.config.read_config()
    bot.globals.displayName = bot.config.botnick

    bot.globals.running = True

    bot.globals.clusters['aws'] = connection.ConnectionHandler(
        'AWS Chat', bot.config.awsServer, bot.config.awsPort)

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

    utils.joinChannel(bot.config.botnick, float('-inf'), 'aws')
    bot.globals.groupChannel = bot.globals.channels[bot.config.botnick]
    if bot.config.owner:
        utils.joinChannel(bot.config.owner, float('-inf'), 'aws')
    db: database.Database
    async with await database.get_database() as db:
        databaseObj: database.DatabaseMain = cast(database.DatabaseMain, db)
        autojoin: AutoJoinChannel
        async for autoJoin in databaseObj.getAutoJoinsChats():
            utils.joinChannel(autoJoin.broadcaster, autoJoin.priority,
                              autoJoin.cluster)


def main(argv: Optional[List[str]]=None) -> int:
    print('{time} Starting'.format(time=utils.now()))
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(initializer())
        coro = asyncio.gather(background.background_tasks(),
                              logging.record_logs(),
                              join.join_manager(),
                              *[c.run_connection() for c
                                in bot.globals.clusters.values()])
        loop.run_until_complete(coro)
        loop.close()
        return 0
    except:
        bot.globals.running = False
        utils.logException()
        raise
    finally:
        print('{time} Ended'.format(time=utils.now()))
