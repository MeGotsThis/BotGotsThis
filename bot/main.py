# Import some necessary libraries.
import asyncio
import importlib
import pkgutil
import types  # noqa: F401
from importlib.abc import PathEntryFinder  # noqa: F401
from typing import Any, Awaitable, Generator, List, Optional, Tuple  # noqa: F401,E501
from typing import cast  # noqa: F401,E501

import aioodbc
import aioredis

import bot
from lib import database
from lib.data import timezones
from lib.data import AutoJoinChannel  # noqa: F401
from . import utils
from .coroutine import background, connection, join, logging


async def initializer() -> None:
    await bot.config.read_config()
    bot.globals.displayName = bot.config.botnick

    bot.globals.pkgs = tuple(bot.config.pkgs)

    bot.globals.running = True

    bot.globals.clusters['aws'] = connection.ConnectionHandler(
        'AWS Chat', bot.config.awsServer, bot.config.awsPort)

    bot.globals.redisPool = await aioredis.create_pool(
        (bot.config.redis['host'], bot.config.redis['port']),
        db=bot.config.redis['db'], password=bot.config.redis['password'],
        minsize=bot.config.redis['connections'],
        maxsize=bot.config.redis['connections'],
    )

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
            if hasattr(mod, '__path__'):
                modules = pkgutil.walk_packages(
                    path=mod.__path__,  # type: ignore
                    prefix=mod.__name__ + '.')
                _importer: PathEntryFinder
                modname: str
                _ispkg: bool
                for _importer, modname, _ispkg in modules:
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
    except Exception:
        bot.globals.running = False
        utils.logException()
        raise
    finally:
        print(f'{utils.now()} Ended')
