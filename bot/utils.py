from . import data
from .coroutine import connection  # noqa: F401
from datetime import datetime, timedelta
from types import TracebackType
from typing import Any, Dict, Iterable, List, Optional, Type, Tuple, Union  # noqa: F401,E501
from lib.api import twitch
import builtins
import bot
import bot.coroutine.logging
import os.path
import sys
import threading
import traceback

ExceptionInfo = Tuple[Optional[type], Optional[BaseException],
                      Optional[TracebackType]]


def now() -> datetime:
    return datetime.utcnow()


def joinChannel(broadcaster: str,
                priority: Union[int, float, str]=float('inf'),
                cluster: str='aws') -> Optional[bool]:
    if not isinstance(broadcaster, str):
        raise TypeError()
    if cluster is None or cluster not in bot.globals.clusters:
        return None
    broadcaster = broadcaster.lower()
    if broadcaster in bot.globals.channels:
        t = min(bot.globals.channels[broadcaster].joinPriority, priority)
        bot.globals.channels[broadcaster].joinPriority = float(t)
        return False
    cluster_: connection.ConnectionHandler = bot.globals.clusters[cluster]
    channel: data.Channel = data.Channel(broadcaster, cluster_, priority)
    bot.globals.channels[broadcaster] = channel
    cluster_.join_channel(channel)
    return True


def partChannel(channel: str) -> None:
    if not isinstance(channel, str):
        raise TypeError()
    if channel in bot.globals.channels:
        bot.globals.channels[channel].part()
        del bot.globals.channels[channel]


def whisper(nick: str, messages: Union[str, Iterable[str]]) -> None:
    cluster = bot.globals.clusters[bot.globals.whisperCluster]
    cluster.messaging.sendWhisper(nick, messages)


def clearAllChat() -> None:
    for c in bot.globals.clusters.values():
        c.messaging.clearAllChat()


async def loadTwitchId(channel: str,
                       timestamp: Optional[datetime]=None) -> bool:
    if timestamp is None:
        timestamp = now()
    if channel in bot.globals.twitchId:
        cacheTime: datetime = bot.globals.twitchIdCache[channel]
        if bot.globals.twitchId[channel] is None:
            if timestamp < cacheTime + timedelta(hours=1):
                return True
        else:
            if timestamp < cacheTime + timedelta(days=1):
                return True
    ids: Optional[Dict[str, str]] = await twitch.getTwitchIds([channel])
    if ids is None:
        return False
    if channel in ids:
        saveTwitchId(channel, ids[channel], timestamp)
    else:
        saveTwitchId(channel, None, timestamp)
    return True


def saveTwitchId(channel: str,
                 id: Optional[str],
                 timestamp: Optional[datetime]=None) -> None:
    if timestamp is None:
        timestamp = now()
    bot.globals.twitchId[channel] = id
    if id is not None:
        bot.globals.twitchIdName[id] = channel
    bot.globals.twitchIdCache[channel] = timestamp


async def loadTwitchCommunityId(id: str,
                                timestamp: Optional[datetime]=None) -> bool:
    if timestamp is None:
        timestamp = now()
    if id in bot.globals.twitchCommunityId:
        name: str = bot.globals.twitchCommunityId[id]
        cacheTime: datetime = bot.globals.twitchCommunityCache[name]
        if bot.globals.twitchCommunity[name] is None:
            if timestamp < cacheTime + timedelta(hours=1):
                return True
        else:
            if timestamp < cacheTime + timedelta(days=1):
                return True
    community: Any  # Optional[twitch.TwitchCommunity]
    community = await twitch.get_community_by_id(id)
    if community is None:
        return False
    saveTwitchCommunity(community.name, community.id, timestamp)
    return True


async def loadTwitchCommunity(name: str,
                              timestamp: Optional[datetime]=None) -> bool:
    if timestamp is None:
        timestamp = now()
    lname: str = name.lower()
    if lname in bot.globals.twitchCommunity:
        cacheTime: datetime = bot.globals.twitchCommunityCache[lname]
        if bot.globals.twitchCommunity[lname] is None:
            if timestamp < cacheTime + timedelta(hours=1):
                return True
        else:
            if timestamp < cacheTime + timedelta(days=1):
                return True
    community: Any  # Optional[twitch.TwitchCommunity]
    community = await twitch.get_community(lname)
    if community is None:
        return False
    saveTwitchCommunity(community.name or name, community.id, timestamp)
    return True


def saveTwitchCommunity(name: Optional[str],
                        id: Optional[str],
                        timestamp: Optional[datetime]=None) -> None:
    if timestamp is None:
        timestamp = now()
    if name is None:
        bot.globals.twitchCommunityId[id] = None
        return
    lname: str = name.lower()
    bot.globals.twitchCommunity[lname] = id
    if id is not None:
        bot.globals.twitchCommunityId[id] = name
    bot.globals.twitchCommunityCache[lname] = timestamp


ENSURE_CLUSTER_UNKNOWN: int = -2
ENSURE_REJOIN: int = -1
ENSURE_CORRECT: int = 0
ENSURE_NOT_JOINED: int = 1


def ensureServer(channel: str,
                 priority: Union[int, float, str, None]=None,
                 cluster: str='aws') -> int:
    if not isinstance(channel, str):
        raise TypeError()
    if cluster is None:
        raise TypeError()
    if channel not in bot.globals.channels:
        return ENSURE_NOT_JOINED
    if cluster not in bot.globals.clusters:
        partChannel(channel)
        return ENSURE_CLUSTER_UNKNOWN
    cluster_: connection.ConnectionHandler = bot.globals.clusters[cluster]
    if cluster_ is bot.globals.channels[channel].connection:
        if priority is not None:
            bot.globals.channels[channel].joinPriority = float(min(
                bot.globals.channels[channel].joinPriority, priority))
        return ENSURE_CORRECT
    if priority is None:
        priority = bot.globals.channels[channel].joinPriority
    partChannel(channel)
    joinChannel(channel, priority, cluster)
    return ENSURE_REJOIN


def print(*args: Any,
          timestamp: Optional[datetime]=None,
          override: bool=False,
          file: Union[bool, str]=False) -> None:
    _timestamp: datetime = timestamp or now()
    if override or bot.config.development:
        builtins.print(_timestamp, *args)

    if file:
        filename: str
        if isinstance(file, str):
            filename = file
        else:
            filename = 'output.log'
        message: str = ' '.join(str(a) for a in args)
        bot.coroutine.logging.log(
            filename,
            f'{_timestamp:%Y-%m-%dT%H:%M:%S.%f} {message}\n')


def property_bool(value: Optional[bool]) -> Optional[str]:
    if value is None:
        return None
    return '1' if value else ''


def logIrcMessage(filename: str,
                  message: str,
                  timestamp: Optional[datetime]=None) -> None:
    if bot.config.ircLogFolder is None:
        return
    timestamp = timestamp or now()
    bot.coroutine.logging.log(
        os.path.join(bot.config.ircLogFolder, filename),
        f'{timestamp:%Y-%m-%dT%H:%M:%S.%f} {message}\n')


def logException(extraMessage: str='',
                 timestamp: Optional[datetime]=None) -> None:
    if bot.config.exceptionLog is None:
        return
    timestamp = timestamp or now()
    exceptType: Optional[Type[BaseException]]  # noqa: E701
    excecption: Optional[BaseException]
    trackback: Optional[TracebackType]
    excep: List[str]

    exceptType, excecption, trackback = sys.exc_info()
    excep = traceback.format_exception(exceptType, excecption, trackback)
    if extraMessage:
        extraMessage += '\n'
    threadName: str = threading.current_thread().name
    exception: str = ''.join(excep)  # noqa: E701
    bot.coroutine.logging.log(
        bot.config.exceptionLog, f'''\
{timestamp:%Y-%m-%dT%H:%M:%S.%f} Exception in thread {threadName}:
{extraMessage}{exception}''')
    if bot.config.development:
        builtins.print(
            timestamp,
            f'''\
Exception in thread {threadName}:
{extraMessage}{exception}''',
            file=sys.stderr)
