import asyncio

from datetime import datetime
from typing import Any, Awaitable, List, Tuple  # noqa: F401

import bot
from bot import data  # noqa: F401
from lib import cache
from lib.helper import timeout

lock: asyncio.Lock = asyncio.Lock()


async def autoRepeatMessage(timestamp: datetime) -> None:
    dataCache: cache.CacheStore
    async with lock, cache.get_cache() as dataCache:
        tasks: List[Awaitable[Any]] = []
        row: Tuple[str, str, str]
        async for row in dataCache.getAutoRepeatToSend():
            broadcaster: str
            name: str
            message: str
            broadcaster, name, message = row
            if broadcaster in bot.globals.channels:
                tasks.append(dataCache.sentAutoRepeat(broadcaster, name))
                channel: data.Channel = bot.globals.channels[broadcaster]
                channel.send(message)
                if channel.isMod:
                    tasks.append(timeout.record_timeout(channel, None, message,
                                                        None, 'autorepeat'))
        if tasks:
            await asyncio.gather(*tasks)
