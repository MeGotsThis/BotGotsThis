import asyncio
import copy
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union  # noqa: F401

import bot
from bot import data, utils  # noqa: F401
from lib import cache
from lib.api import twitch
from lib.database import DatabaseMain


async def checkTwitchIds(timestamp: datetime) -> None:
    if not bot.globals.channels:
        return
    dataCache: cache.CacheStore
    async with cache.get_cache() as dataCache:
        channels: List[str] = list(bot.globals.channels.keys())
        await dataCache.twitch_load_ids(channels)


async def checkStreamsAndChannel(timestamp: datetime) -> None:
    if not bot.globals.channels:
        return
    dataCache: cache.CacheStore
    async with cache.get_cache() as dataCache:
        channels: Dict[str, data.Channel] = copy.copy(bot.globals.channels)
        onlineStreams: Optional[twitch.OnlineStreams]
        onlineStreams = await twitch.active_streams(channels.keys(),
                                                    data=dataCache)
        if onlineStreams is None:
            return
        communityIds: Set[str] = set()
        channel: str
        for channel in onlineStreams:
            chat: data.Channel = channels[channel]
            chat.twitchCache = timestamp
            (chat.streamingSince, chat.twitchStatus,
             chat.twitchGame, chat.community) = onlineStreams[channel]
            communityId: str
            for communityId in chat.community:
                communityIds.add(communityId)

        for channel in channels:
            if channel in onlineStreams:
                continue
            channels[channel].streamingSince = None

        await asyncio.gather(*[dataCache.twitch_load_community_id(id)
                               for id in communityIds])


async def checkOfflineChannels(timestamp: datetime) -> None:
    channels: Dict[str, data.Channel] = copy.copy(bot.globals.channels)
    if not channels:
        return
    channel: data.Channel
    for channel in channels.values():
        if 'offlineLock' not in channel.sessionData:
            channel.sessionData['offlineLock'] = asyncio.Lock()
    cacheDuration: timedelta = timedelta(seconds=300)
    offlineChannels: List[data.Channel]
    offlineChannels = [ch for ch in channels.values()
                       if (not ch.isStreaming
                           and timestamp - ch.twitchCache >= cacheDuration
                           and not ch.sessionData['offlineLock'].locked())]
    if not offlineChannels:
        return
    if 'offlineCheck' not in bot.globals.globalSessionData:
        bot.globals.globalSessionData['offlineCheck'] = []
    bot.globals.globalSessionData['offlineCheck'] = [
        t for t in bot.globals.globalSessionData['offlineCheck']
        if t >= timestamp - timedelta(minutes=1)]
    if len(bot.globals.globalSessionData['offlineCheck']) >= 40:
        return
    chat: data.Channel = random.choice(offlineChannels)
    chat.twitchCache = timestamp
    dataCache: cache.CacheStore
    async with chat.sessionData['offlineLock'], cache.get_cache() as dataCache:
        current: Optional[twitch.TwitchStatus]
        current = await twitch.channel_properties(chat.channel)
        if current is None:
            chat.twitchCache = (timestamp - cacheDuration
                                + timedelta(seconds=60))
            return
        (chat.streamingSince, chat.twitchStatus,
         chat.twitchGame, shouldBeNone) = current
        communities: Optional[List[twitch.TwitchCommunity]]
        communities = await twitch.channel_community(chat.channel)
        if communities is not None:
            community: twitch.TwitchCommunity
            chat.community = [community.id for community in communities]
            await asyncio.gather(
                *[dataCache.twitch_save_community(comm.id, comm.name)
                  for comm in communities]
            )
        bot.globals.globalSessionData['offlineCheck'].append(timestamp)


async def checkChatServers(timestamp: datetime) -> None:
    cooldown: timedelta = timedelta(seconds=3600)
    channels: Dict[str, data.Channel] = copy.copy(bot.globals.channels)
    toCheck: List[str] = [c for c, ch in channels.items()
                          if (timestamp - ch.serverCheck >= cooldown)]
    if not toCheck:
        return
    channel: str = random.choice(toCheck)
    channels[channel].serverCheck = timestamp
    cluster: Optional[str] = await twitch.chat_server(channel)
    if cluster is None:
        return
    if (cluster in bot.globals.clusters
            and bot.globals.clusters[cluster] is channels[channel].connection):
        return
    db: DatabaseMain
    async with DatabaseMain.acquire() as db:
        priority: Union[int, float]
        priority = await db.getAutoJoinsPriority(channel)
        utils.ensureServer(channel, priority, cluster)
        await db.setAutoJoinServer(channel, cluster)
