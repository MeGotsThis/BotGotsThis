from . import data
from bot import config, globals
from datetime import datetime
from typing import List, Optional, TextIO, Tuple, Union
import os.path
import sys
import threading
import traceback


def joinChannel(broadcaster: str,
                priority: Union[int, float]=float('inf'),
                cluster: str='aws') -> bool:
    if cluster is None or cluster not in globals.clusters:
        return False
    broadcaster = broadcaster.lower()
    if broadcaster in globals.channels:
        t = min(globals.channels[broadcaster].joinPriority, priority)
        globals.channels[broadcaster].joinPriority = t
        return False
    globals.channels[broadcaster] = data.Channel(
        broadcaster, globals.clusters[cluster], priority)
    globals.clusters[cluster].joinChannel(globals.channels[broadcaster])
    return True


def partChannel(channel: str) -> None:
    if channel in globals.channels:
        globals.channels[channel].part()
        del globals.channels[channel]


def whisper(nick: str, message: str) -> None:
    cluster = globals.clusters[globals.whisperCluster]
    cluster.messaging.sendWhisper(nick, message)


def clearAllChat() -> None:
    for c in globals.clusters.values():
        c.messaging.clearAllChat()

ENSURE_CLUSTER_UNKNOWN = -3  # type: int
ENSURE_CLUSTER_NONE = -2  # type: int
ENSURE_REJOIN = -1  # type: int
ENSURE_CORRECT = 0  # type: int
ENSURE_NOT_JOINED = 1  # type: int


def ensureServer(channel: str,
                 priority: Union[int, float]=float('inf'),
                 cluster: str='aws') -> int:
    if channel not in globals.channels:
        return ENSURE_NOT_JOINED
    if cluster is None:
        return ENSURE_CLUSTER_NONE
    if cluster not in globals.clusters:
        partChannel(channel)
        return ENSURE_CLUSTER_UNKNOWN
    if globals.clusters[cluster] is globals.channels[channel].socket:
        globals.channels[channel].joinPriority = min(
            globals.channels[channel].joinPriority, priority)
        return ENSURE_CORRECT
    partChannel(channel)
    joinChannel(channel, priority, cluster)
    return ENSURE_REJOIN


def logIrcMessage(filename: str,
                  message: str,
                  timestamp: Optional[datetime]=None) -> None:
    if config.ircLogFolder is None:
        return
    timestamp = timestamp or datetime.utcnow()
    with open(os.path.join(config.ircLogFolder, filename), 'a',
              encoding='utf-8') as file:  # --type: TextIO
        file.write(
            '{time:%Y-%m-%dT%H:%M:%S.%f} {message}\n'.format(
                time=timestamp, message=message))


def logException(extraMessage: str=None,
                 timestamp: Optional[datetime]=None) -> None:
    if config.exceptionLog is None:
        return
    timestamp = timestamp or datetime.utcnow()
    exceptInfo = sys.exc_info()  # type: Tuple[Optional[type], Optional[BaseException], Optional[traceback.TracebackType]]
    excep = traceback.format_exception(*exceptInfo)  # type: ignore -- List[traceback.TracebackException]
    with open(config.exceptionLog, 'a', encoding='utf-8') as file:  # --type: TextIO
        if extraMessage and extraMessage[-1] != '\n':
            extraMessage += '\n'
        file.write(
            '{time:%Y-%m-%dT%H:%M:%S.%f} Exception in thread {thread}:\n'
            '{extra}{exception}'.format(
                time=timestamp, thread=threading.current_thread().name,  # type: ignore --
                extra=extraMessage, exception=''.join(excep)))
