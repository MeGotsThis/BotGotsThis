# Import some necessary libraries.
import asyncio
import aioodbc
import bot
import importlib
import pkgutil
import types  # noqa: F401
from itertools import chain
from importlib.abc import PathEntryFinder  # noqa: F401
from lib import database
from lib.data import timezones
from lib.database import AutoJoinChannel  # noqa: F401
from typing import Any, Awaitable, Generator, List, Optional, Tuple  # noqa: F401,E501
from typing import cast  # noqa: F401,E501
from . import utils
from .coroutine import background, connection, join, logging


async def initializer() -> None:
    await bot.config.read_config()
    bot.globals.displayName = bot.config.botnick

    bot.globals.pkgs = tuple(bot.config.pkgs)

    bot.globals.running = True

    bot.globals.clusters['aws'] = connection.ConnectionHandler(
        'AWS Chat', bot.config.awsServer, bot.config.awsPort)

    schema: database.Schema
    for schema in database.Schema:
        pool: aioodbc.Pool
        pool = await aioodbc.create_pool(
            minsize=bot.config.connections[schema.value],
            maxsize=bot.config.connections[schema.value],
            dsn=bot.config.database[schema.value])
        bot.globals.connectionPools[schema.value] = pool

    pkg: str
    modules: Generator[Tuple[PathEntryFinder, str, bool], None, None]
    for pkg in bot.globals.pkgs:
        try:
            mod: types.ModuleType
            mod = importlib.import_module('pkg.' + pkg + '.autoload')
            modules = pkgutil.walk_packages(path=mod.__path__,  # type: ignore
                                            prefix=mod.__name__ + '.')
            importer: PathEntryFinder
            modname: str
            ispkg: bool
            for importer, modname, ispkg in chain(modules):
                importlib.import_module(modname)
        except ModuleNotFoundError:
            pass

    utils.joinChannel(bot.config.botnick, float('-inf'), 'aws')
    bot.globals.groupChannel = bot.globals.channels[bot.config.botnick]
    if bot.config.owner:
        utils.joinChannel(bot.config.owner, float('-inf'), 'aws')

    db: database.Database
    async with database.get_database() as db:
        databaseObj: database.DatabaseMain = cast(database.DatabaseMain, db)
        autojoin: AutoJoinChannel
        async for autoJoin in databaseObj.getAutoJoinsChats():
            utils.joinChannel(autoJoin.broadcaster, autoJoin.priority,
                              autoJoin.cluster)


async def finalizer() -> None:
    schema: database.Schema
    for schema in database.Schema:
        bot.globals.connectionPools[schema.value].close()
        await bot.globals.connectionPools[schema.value].wait_closed()


def main(argv: Optional[List[str]]=None) -> int:
    print(f'{utils.now()} Starting')
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(initializer())
        coro: Awaitable[List[Any]] = asyncio.gather(
            timezones.load_timezones(),
            background.background_tasks(),
            logging.record_logs(),
            join.join_manager(),
            *[c.run_connection() for c in bot.globals.clusters.values()])
        loop.run_until_complete(coro)
        if asyncio.Task.all_tasks():
            asyncio.wait_for(asyncio.gather(*asyncio.Task.all_tasks()), 10)
        loop.run_until_complete(finalizer())
        loop.close()
        return 0
    except:
        bot.globals.running = False
        utils.logException()
        raise
    finally:
        print(f'{utils.now()} Ended')
