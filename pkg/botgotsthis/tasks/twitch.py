import bot
import copy
import random
from bot import data, utils  # noqa: F401
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, cast  # noqa: F401
from lib.api import twitch
from lib import database


async def checkTwitchIds(timestamp: datetime) -> None:
    if not bot.globals.channels:
        return
    twitchIds: Dict[str, Optional[str]] = copy.copy(bot.globals.twitchId)
    channels: List[str] = [c for c in bot.globals.channels
                           if c not in twitchIds]
    cacheDuration: timedelta = timedelta(hours=1)
    channels += [c for c in twitchIds
                 if c not in channels
                 if bot.globals.twitchIdCache[c] + cacheDuration <= timestamp]
    if not channels:
        return

    ids: Optional[Dict[str, str]] = await twitch.getTwitchIds(channels)
    if ids is None:
        return
    channel: str
    id: str
    for channel, id in ids.items():
        utils.saveTwitchId(channel, id, timestamp)
    for channel in bot.globals.channels:
        if channel in ids:
            continue
        if channel in bot.globals.twitchIdCache:
            cacheExpired: datetime
            cacheExpired = bot.globals.twitchIdCache[channel] + cacheDuration
            if cacheExpired >= timestamp:
                continue
        utils.saveTwitchId(channel, None, timestamp)


async def checkStreamsAndChannel(timestamp: datetime) -> None:
    if not bot.globals.channels:
        return
    channels: Dict[str, data.Channel] = copy.copy(bot.globals.channels)
    onlineStreams: Optional[twitch.OnlineStreams]
    onlineStreams = await twitch.active_streams(channels.keys())
    if onlineStreams is None:
        return
    channel: str
    for channel in onlineStreams:
        chat: data.Channel = channels[channel]
        chat.twitchCache = timestamp
        (chat.streamingSince, chat.twitchStatus,
         chat.twitchGame, chat.community) = onlineStreams[channel]
        communityId: str
        for communityId in chat.community:
            await bot.utils.loadTwitchCommunity(communityId)

    for channel in channels:
        if channel in onlineStreams:
            continue
        channels[channel].streamingSince = None


async def checkOfflineChannels(timestamp: datetime) -> None:
    if not bot.globals.channels:
        return
    cacheDuration: timedelta = timedelta(seconds=300)
    offlineChannels: List[data.Channel]
    offlineChannels = [ch for ch in bot.globals.channels.values()
                       if (not ch.isStreaming
                           and timestamp - ch.twitchCache >= cacheDuration)]
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
    current: Optional[twitch.TwitchStatus]
    current = await twitch.channel_properties(chat.channel)
    if current is None:
        chat.twitchCache = timestamp - cacheDuration + timedelta(seconds=60)
        return
    (chat.streamingSince, chat.twitchStatus,
     chat.twitchGame, shouldBeNone) = current
    communities: Optional[List[twitch.TwitchCommunity]]
    communities = await twitch.channel_community(chat.channel)
    if communities is not None:
        community: twitch.TwitchCommunity
        chat.community = [community.id for community in communities]
        for community in communities:
            bot.utils.saveTwitchCommunity(community.name, community.id,
                                          timestamp)
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
    db: database.Database
    async with database.get_database() as db:
        database_: database.DatabaseMain = cast(database.DatabaseMain, db)
        priority: Union[int, float]
        priority = await database_.getAutoJoinsPriority(channel)
        utils.ensureServer(channel, priority, cluster)
        await database_.setAutoJoinServer(channel, cluster)
