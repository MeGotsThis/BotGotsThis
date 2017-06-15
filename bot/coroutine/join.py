import asyncio

import bot.config
import bot.globals

from datetime import datetime, timedelta
from collections import deque
from typing import Dict, Deque, List, Optional, Set

from bot import data, utils
from bot.twitchmessage import IrcMessage, IrcMessageParams

joinDuration: timedelta = timedelta(seconds=10.05)
_joinTimes: Deque[datetime] = deque()
_channelJoined: Set[str] = set()


async def join_manager():
    name = 'Channel Join Manager'
    print('{time} Starting {name}'.format(time=utils.now(), name=name))
    while bot.globals.running:
        try:
            join_a_channel()
            await asyncio.sleep(1 / bot.config.joinPerSecond)
        except:
            utils.logException()
    print('{time} Ending {name}'.format(time=utils.now(), name=name))


def join_a_channel() -> None:
    if not _can_process():
        return

    channels: Dict[str, data.Channel] = _connected_channels()
    notJoined: Set[str] = set(channels.keys()) - _channelJoined
    if not notJoined:
        return

    broadcaster: Optional[str]
    broadcaster = _get_join_with_lowest_priority(channels, notJoined)
    if broadcaster is None:
        return
    chat: data.Channel = channels[broadcaster]
    if chat.socket is None:
        return
    ircCommand: IrcMessage = IrcMessage(
        None, None, 'JOIN', IrcMessageParams(chat.ircChannel))
    chat.socket.queueWrite(ircCommand, channel=chat)
    _channelJoined.add(chat.channel)


def connected(socket: 'data.SocketHandler') -> None:
    _joinTimes.append(utils.now())


def disconnected(socket: 'data.SocketHandler') -> None:
    global _channelJoined
    _channelJoined -= socket.channels.keys()


def on_part(channel: str) -> None:
    _channelJoined.discard(channel)


def record_join() -> None:
    timestamp: datetime = utils.now()
    _joinTimes.append(timestamp)


def _can_process() -> bool:
    timestamp: datetime = utils.now()
    while _joinTimes and (timestamp - _joinTimes[0]) > joinDuration:
        _joinTimes.popleft()
    return len(_joinTimes) < bot.config.joinLimit


def _connected_channels() -> Dict[str, 'data.Channel']:
    channels: Dict[str, data.Channel] = {}
    socketManager: data.SocketHandler
    chans: Dict[str, data.Channel]
    chan: str
    for socketManager in bot.globals.clusters.values():
        if not socketManager.isConnected:
            continue
        chans = socketManager.channels
        for chan in chans:
            channels[chan] = chans[chan]
    return channels


def _get_join_with_lowest_priority(
        channels: Dict[str, 'data.Channel'],
        notJoinedChannels: Set[str]) -> Optional[str]:
    notJoined: List[data.Channel]
    notJoined = [channels[nc] for nc in notJoinedChannels]
    if not notJoined:
        return None
    priority: float = float(min(ch.joinPriority for ch in notJoined))
    return [ch.channel for ch in notJoined
            if ch.joinPriority == priority][0]
