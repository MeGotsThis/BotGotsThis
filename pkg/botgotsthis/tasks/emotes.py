import asyncio
import bot
import copy
import random
from bot import data  # noqa: F401
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set  # noqa: F401
from lib.api import bttv
from lib import cache

twitchLock = asyncio.Lock()
ffzGlobalLock = asyncio.Lock()


async def refreshTwitchGlobalEmotes(timestamp: datetime) -> None:
    if twitchLock.locked():
        return
    dataCache: cache.CacheStore
    async with twitchLock, cache.get_cache() as dataCache:
        emoteSet: Set[int] = await dataCache.twitch_get_bot_emote_set()
        if emoteSet is None:
            return
        await dataCache.twitch_load_emotes(emoteSet, background=True)


async def refreshFrankerFaceZEmotes(timestamp: datetime) -> None:
    await asyncio.wait([refreshFfzGlobalEmotes(timestamp),
                        refreshFfzRandomBroadcasterEmotes(timestamp)])


async def refreshFfzGlobalEmotes(timestamp: datetime) -> None:
    if ffzGlobalLock.locked():
        return
    dataCache: cache.CacheStore
    async with ffzGlobalLock, cache.get_cache() as dataCache:
        await dataCache.ffz_load_global_emotes(background=True)


async def refreshFfzRandomBroadcasterEmotes(timestamp: datetime) -> None:
    channels: Dict[str, data.Channel] = copy.copy(bot.globals.channels)
    channel: data.Channel
    for channel in channels.values():
        if 'ffzLock' not in channel.sessionData:
            channel.sessionData['ffzLock'] = asyncio.Lock()
    dataCache: cache.CacheStore
    async with cache.get_cache() as dataCache:
        ttlChannels: Dict[str, int] = {
            b: t async for b, t in dataCache.ffz_get_cached_broadcasters()
        }
        toUpdate: List[data.Channel]
        toUpdate = [chan for chan in channels.values()
                    if (chan.channel not in ttlChannels
                        or ttlChannels[chan.channel] < 30)
                    and chan.isStreaming
                    and not chan.sessionData['ffzLock'].locked()]
        if not toUpdate:
            toUpdate = [chan for chan in channels.values()
                        if (chan.channel not in ttlChannels
                            or ttlChannels[chan.channel] < 30)
                        and not chan.isStreaming
                        and not chan.sessionData['ffzLock'].locked()]
        if toUpdate:
            channel = random.choice(toUpdate)
            async with channel.sessionData['ffzLock']:
                await dataCache.ffz_load_broadcaster_emotes(channel.channel,
                                                            background=True)


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
