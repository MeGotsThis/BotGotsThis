import bot.config
import bot.globals
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set
from .. import data, utils
from ..twitchmessage import IrcMessage, IrcMessageParams

joinDuration = timedelta(seconds=10.05)


class JoinThread(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self, **kwargs)  # type: ignore
        self._joinTimes = []  # type: List[datetime]
        self._joinTimesLock = threading.Lock()  # type: threading.Lock
        self._channelJoined = set()  # type: Set[str]
        self._channelsLock = threading.Lock()  # type: threading.Lock

    @property
    def canProcess(self) -> bool:
        timestamp = utils.now()
        with self._joinTimesLock:
            self._joinTimes = [t for t in self._joinTimes
                               if timestamp - t <= joinDuration]
            return len(self._joinTimes) < bot.config.joinLimit

    @property
    def connectedChannels(self) -> 'Dict[str, data.Channel]':
        channels = {}  # type: Dict[str, data.Channel]
        for socketThread in bot.globals.clusters.values():  # --type: SocketsThread
            if socketThread.isConnected:
                chans = socketThread.channels
                for chan in chans:  # --type: Channel
                    channels[chan] = chans[chan]
        return channels

    def run(self) -> None:
        print('{time} Starting {name}'.format(
            time=utils.now(), name=self.__class__.__name__))
        while bot.globals.running:
            try:
                self.process()
                time.sleep(1 / bot.config.joinPerSecond)
            except:
                utils.logException()
        print('{time} Ending {name}'.format(
            time=utils.now(), name=self.__class__.__name__))

    def process(self) -> None:
        if not self.canProcess:
            return

        channels = self.connectedChannels  # type: Dict[str, data.Channel]
        with self._channelsLock:
            notJoined = set(channels.keys()) - self._channelJoined  # type: Set[str]
            if not notJoined:
                return
            
            broadcaster = self._getJoinWithLowestPriority(channels, notJoined)  # type: str
            chat = channels[broadcaster]  # type: data.Channel
            if chat.socket is not None:
                ircCommand = IrcMessage(
                    None, None, 'JOIN', IrcMessageParams(chat.ircChannel)) # type: IrcMessage
                chat.socket.queueWrite(ircCommand, channel=chat)
                self._channelJoined.add(chat.channel)

    def connected(self, socket: 'data.Socket') -> None:
        with self._joinTimesLock:
            self._joinTimes.append(utils.now())
    
    def disconnected(self, socket: 'data.Socket') -> None:
        with self._channelsLock:
            self._channelJoined -= socket.channels.keys()
    
    def onPart(self, channel: str) -> None:
        with self._channelsLock:
            self._channelJoined.discard(channel)
    
    def recordJoin(self) -> None:
        timestamp = utils.now()  # type: datetime
        with self._joinTimesLock:
            self._joinTimes.append(timestamp)
    
    @staticmethod
    def _getJoinWithLowestPriority(channels: Dict[str, 'data.Channel'],
                                   notJoinedChannels: Set[str]) -> str:
        notJoined = [channels[nc] for nc in notJoinedChannels]  # type: List[data.Channel]
        if not notJoined:
            return None
        priority = float(min(ch.joinPriority for ch in notJoined)) # type: float
        return [ch.channel for ch in notJoined
                if ch.joinPriority == priority][0]
