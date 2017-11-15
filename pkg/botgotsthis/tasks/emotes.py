import asyncio
import copy
import random
from datetime import datetime
from typing import Dict, List, Set  # noqa: F401

import bot
from bot import data  # noqa: F401
from lib import cache

twitchLock = asyncio.Lock()
ffzGlobalLock = asyncio.Lock()
bttvGlobalLock = asyncio.Lock()


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
        ttlChannels: Dict[str, int]
        ttlChannels = await dataCache.ffz_get_cached_broadcasters()
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
    if bttvGlobalLock.locked():
        return
    dataCache: cache.CacheStore
    async with bttvGlobalLock, cache.get_cache() as dataCache:
        await dataCache.bttv_load_global_emotes(background=True)


async def refreshBttvRandomBroadcasterEmotes(timestamp: datetime) -> None:
    channels: Dict[str, data.Channel] = copy.copy(bot.globals.channels)
    channel: data.Channel
    for channel in channels.values():
        if 'bttvLock' not in channel.sessionData:
            channel.sessionData['bttvLock'] = asyncio.Lock()
    dataCache: cache.CacheStore
    async with cache.get_cache() as dataCache:
        ttlChannels: Dict[str, int]
        ttlChannels = await dataCache.bttv_get_cached_broadcasters()
        toUpdate: List[data.Channel]
        toUpdate = [chan for chan in channels.values()
                    if (chan.channel not in ttlChannels
                        or ttlChannels[chan.channel] < 30)
                    and chan.isStreaming
                    and not chan.sessionData['bttvLock'].locked()]
        if not toUpdate:
            toUpdate = [chan for chan in channels.values()
                        if (chan.channel not in ttlChannels
                            or ttlChannels[chan.channel] < 30)
                        and not chan.isStreaming
                        and not chan.sessionData['bttvLock'].locked()]
        if toUpdate:
            channel = random.choice(toUpdate)
            async with channel.sessionData['bttvLock']:
                await dataCache.bttv_load_broadcaster_emotes(channel.channel,
                                                             background=True)
