from . import data
from datetime import datetime
from types import TracebackType
from typing import Any, Iterable, Optional, Tuple, Union
import builtins
import bot.config
import bot.globals
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
    bot.globals.channels[broadcaster] = data.Channel(
        broadcaster, bot.globals.clusters[cluster], priority)
    bot.globals.clusters[cluster].joinChannel(bot.globals.channels[broadcaster])
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

ENSURE_CLUSTER_UNKNOWN = -2  # type: int
ENSURE_REJOIN = -1  # type: int
ENSURE_CORRECT = 0  # type: int
ENSURE_NOT_JOINED = 1  # type: int


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
    if bot.globals.clusters[cluster] is bot.globals.channels[channel].socket:
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
          override: bool=True,
          file: Union[bool, str]=False) -> None:
    _timestamp = timestamp or now()  # type: datetime
    if not override or bot.config.development:
        builtins.print(_timestamp, *args)

    if file:
        if isinstance(file, str):
            filename = file  # type: str
        else:
            filename = 'output.log'
        bot.globals.logging.log(
            filename,
            '{time:%Y-%m-%dT%H:%M:%S.%f} {message}\n'.format(
                time=_timestamp, message=''.join(str(a) for a in args)))


def logIrcMessage(filename: str,
                  message: str,
                  timestamp: Optional[datetime]=None) -> None:
    if bot.config.ircLogFolder is None:
        return
    timestamp = timestamp or now()
    bot.globals.logging.log(
        os.path.join(bot.config.ircLogFolder, filename),
        '{time:%Y-%m-%dT%H:%M:%S.%f} {message}\n'.format(
            time=timestamp, message=message))


def logException(extraMessage: str='',
                 timestamp: Optional[datetime]=None) -> None:
    if bot.config.exceptionLog is None:
        return
    timestamp = timestamp or now()
    exceptInfo = sys.exc_info()  # type: ExceptionInfo
    excep = traceback.format_exception(*exceptInfo)  # type: ignore
    if extraMessage:
        extraMessage += '\n'
    bot.globals.logging.log(
        bot.config.exceptionLog,
        '{time:%Y-%m-%dT%H:%M:%S.%f} Exception in thread {thread}:\n'
        '{extra}{exception}'.format(
            time=timestamp, thread=threading.current_thread().name,
            extra=extraMessage, exception=''.join(excep)))
    if bot.config.development:
        builtins.print(
            timestamp,
            'Exception in thread {thread}:\n{extra}{exception}'.format(
                thread=threading.current_thread().name,
                extra=extraMessage, exception=''.join(excep)),
            file=sys.stderr)
