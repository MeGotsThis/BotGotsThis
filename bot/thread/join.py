import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set
from ..data import channel, socket
from .. import config
from .. import globals
from .. import utils
from ..twitchmessage.ircmessage import IrcMessage
from ..twitchmessage.ircparams import IrcMessageParams

joinDuration = timedelta(seconds=10.05)


class JoinThread(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self, **kwargs)
        self._joinTimes = []  # type: List[datetime]
        self._joinTimesLock = threading.Lock()  # type: threading.Lock
        self._channelJoined = set()  # type: Set[str]
        self._channelsLock = threading.Lock()  # type: threading.Lock
    
    def run(self) -> None:
        print('{time} Starting {name}'.format(
            time=datetime.utcnow(), name=self.__class__.__name__))
        while globals.running:
            try:
                self.process()
                time.sleep(1 / config.joinPerSecond)
            except:
                utils.logException()
        print('{time} Ending {name}'.format(
            time=datetime.utcnow(), name=self.__class__.__name__))

    def process(self) -> None:
        timestamp = datetime.utcnow()  # type: datetime
        with self._joinTimesLock:
            self._joinTimes = [t for t in self._joinTimes
                               if timestamp - t <= joinDuration]
            if len(self._joinTimes) >= config.joinLimit:
                return
        
        channels = {}  # type: Dict[str, channel.Channel]
        for socketThread in globals.clusters.values():  # --type: SocketsThread
            if socketThread.isConnected:
                chans = socketThread.channels
                for chan in chans:  # --type: Channel
                    channels[chan] = chans[chan]
        with self._channelsLock:
            notJoined = set(channels.keys() - self._channelJoined)  # type: Set[str]
            if not notJoined:
                return
            
            broadcaster = self._getJoinWithLowestPriority(channels, notJoined)  # type: str
            chat = channels[broadcaster]  # type: channel.Channel
            if chat.socket is not None:
                ircCommand = IrcMessage(
                    None, None, 'JOIN', IrcMessageParams(chat.ircChannel)) # type: IrcMessage
                chat.socket.queueWrite(ircCommand, channel=chat)
                self._channelJoined.add(chat.channel)
    
    def connected(self, socket: socket.Socket) -> None:
        with self._joinTimesLock:
            self._joinTimes.append(datetime.utcnow())
    
    def disconnected(self, socket: socket.Socket) -> None:
        with self._channelsLock:
            self._channelJoined -= socket.channels.keys()
    
    def part(self, channel: str) -> None:
        with self._channelsLock:
            self._channelJoined.discard(channel)
    
    def recordJoin(self) -> None:
        timestamp = datetime.utcnow()  # type: datetime
        with self._joinTimesLock:
            self._joinTimes.append(timestamp)
    
    @staticmethod
    def _getJoinWithLowestPriority(channels: Dict[str, channel.Channel],
                                   notJoinedChannels: Set[str]) -> str:
        priority = float(min(float(channels[c].joinPriority) for c
                             in notJoinedChannels)) # type: float
        return [c for c in notJoinedChannels
                if channels[c].joinPriority == priority][0]
