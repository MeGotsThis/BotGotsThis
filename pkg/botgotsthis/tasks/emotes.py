import asyncio
import bot
import copy
import random
from bot import data  # noqa: F401
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set  # noqa: F401
from lib.api import bttv
from lib.api import ffz
from lib import cache

twitchLock = asyncio.Lock()


async def refreshTwitchGlobalEmotes(timestamp: datetime) -> None:
    if twitchLock.locked():
        return
    async with twitchLock:
        cacheStore: cache.CacheStore
        async with cache.get_cache() as cacheStore:
            emoteSet: Set[int] = await cacheStore.twitch_get_bot_emote_set()
            if emoteSet is None:
                return
            await cacheStore.twitch_load_emotes(emoteSet, background=True)


async def refreshFrankerFaceZEmotes(timestamp: datetime) -> None:
    await asyncio.wait([refreshFfzGlobalEmotes(timestamp),
                        refreshFfzRandomBroadcasterEmotes(timestamp)])


async def refreshFfzGlobalEmotes(timestamp: datetime) -> None:
    if timestamp - bot.globals.globalFfzEmotesCache >= timedelta(hours=1):
        emotes: Optional[Dict[int, str]]
        bot.globals.globalFfzEmotesCache = timestamp
        emotes = await ffz.getGlobalEmotes()
        if emotes is not None:
            bot.globals.globalFfzEmotes = emotes


async def refreshFfzRandomBroadcasterEmotes(timestamp: datetime) -> None:
    channels: Dict[str, data.Channel] = copy.copy(bot.globals.channels)
    toUpdate: List[data.Channel]
    toUpdate = [chan for chan in channels.values()
                if timestamp - chan.ffzCache >= timedelta(hours=1)
                and chan.isStreaming]
    if not toUpdate:
        toUpdate = [chan for chan in channels.values()
                    if timestamp - chan.ffzCache >= timedelta(hours=1)
                    and not chan.isStreaming]
    if toUpdate:
        await random.choice(toUpdate).updateFfzEmotes()


async def refreshBetterTwitchTvEmotes(timestamp: datetime) -> None:
    await asyncio.wait([refreshBttvGlobalEmotes(timestamp),
                        refreshBttvRandomBroadcasterEmotes(timestamp)])


async def refreshBttvGlobalEmotes(timestamp: datetime) -> None:
    if timestamp - bot.globals.globalBttvEmotesCache >= timedelta(hours=1):
        emotes: Optional[Dict[str, str]]
        bot.globals.globalBttvEmotesCache = timestamp
        emotes = await bttv.getGlobalEmotes()
        if emotes is not None:
            bot.globals.globalBttvEmotes = emotes


async def refreshBttvRandomBroadcasterEmotes(timestamp: datetime) -> None:
    channels: Dict[str, data.Channel] = copy.copy(bot.globals.channels)
    toUpdate: List[data.Channel]
    toUpdate = [chan for chan in channels.values()
                if timestamp - chan.bttvCache >= timedelta(hours=1)
                and chan.isStreaming]
    if not toUpdate:
        toUpdate = [chan for chan in channels.values()
                    if timestamp - chan.bttvCache >= timedelta(hours=1)
                    and not chan.isStreaming]
    if toUpdate:
        await random.choice(toUpdate).updateBttvEmotes()
