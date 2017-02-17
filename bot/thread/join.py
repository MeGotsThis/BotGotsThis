import bot.config
import bot.globals
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from .. import data, utils
from ..twitchmessage import IrcMessage, IrcMessageParams

joinDuration = timedelta(seconds=10.05)


class JoinThread(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self, **kwargs)
        self._joinTimes: List[datetime] = []
        self._joinTimesLock: threading.Lock = threading.Lock()
        self._channelJoined: Set[str] = set()
        self._channelsLock: threading.Lock = threading.Lock()

    @property
    def canProcess(self) -> bool:
        timestamp = utils.now()
        with self._joinTimesLock:
            self._joinTimes = [t for t in self._joinTimes
                               if timestamp - t <= joinDuration]
            return len(self._joinTimes) < bot.config.joinLimit

    @property
    def connectedChannels(self) -> Dict[str, 'data.Channel']:
        channels: Dict[str, data.Channel] = {}
        socketThread: data.Socket
        chans: Dict[str, data.Channel]
        chan: str
        for socketThread in bot.globals.clusters.values():
            if not socketThread.isConnected:
                continue
            chans = socketThread.channels
            for chan in chans:
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

        channels: Dict[str, data.Channel] = self.connectedChannels
        with self._channelsLock:
            notJoined: Set[str] = set(channels.keys()) - self._channelJoined
            if not notJoined:
                return

            broadcaster: Optional[str]
            broadcaster = self._getJoinWithLowestPriority(channels, notJoined)
            if broadcaster is None:
                return
            chat: data.Channel = channels[broadcaster]
            if chat.socket is None:
                return
            ircCommand: IrcMessage = IrcMessage(
                None, None, 'JOIN', IrcMessageParams(chat.ircChannel))
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
        timestamp: datetime = utils.now()
        with self._joinTimesLock:
            self._joinTimes.append(timestamp)
    
    @staticmethod
    def _getJoinWithLowestPriority(
            channels: Dict[str, 'data.Channel'],
            notJoinedChannels: Set[str]) -> Optional[str]:
        notJoined: List[data.Channel]
        notJoined = [channels[nc] for nc in notJoinedChannels]
        if not notJoined:
            return None
        priority: float = float(min(ch.joinPriority for ch in notJoined))
        return [ch.channel for ch in notJoined
                if ch.joinPriority == priority][0]
