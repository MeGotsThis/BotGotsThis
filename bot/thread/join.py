from .. import config
from .. import globals
from .. import utils
from ..twitchmessage.ircmessage import IrcMessage
from ..twitchmessage.ircparams import IrcMessageParams
import threading
import traceback
import datetime
import os.path
import time
import sys

class JoinThread(threading.Thread):
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
        self._joinTimes = []
        self._joinTimesLock = threading.Lock()
        self._channelJoined = set()
        self._channelsLock = threading.Lock()
    
    def run(self):
        print('{time} Starting {name}'.format(
            time=datetime.datetime.utcnow(), name=self.__class__.__name__))
        joinDuration = datetime.timedelta(seconds=10.05)
        while globals.running:
            try:
                utcnow = datetime.datetime.utcnow()
                with self._joinTimesLock:
                    self._joinTimes = [t for t in self._joinTimes
                                       if utcnow - t <= joinDuration]
                    if len(self._joinTimes) >= config.joinLimit:
                        time.sleep(1 / config.joinPerSecond)
                        continue
                
                channels = {}
                for socketThread in globals.clusters.values():
                    if socketThread.isConnected:
                        chans = socketThread.channels
                        for chan in chans:
                            channels[chan] = chans[chan]
                with self._channelsLock:
                    notJoined = set(channels.keys() - self._channelJoined)
                    
                    if not notJoined:
                        time.sleep(1 / config.joinPerSecond)
                        continue
                    
                    params = channels, notJoined
                    broadcaster = self._getJoinWithLowestPriority(*params)
                    chat = channels[broadcaster]
                    if chat.socket is not None:
                        ircCommand = IrcMessage(
                            command='JOIN',
                            params=IrcMessageParams(
                                middle=chat.ircChannel))
                        params = ircCommand, chat.ircChannel
                        chat.socket.queueWrite(*params)
                        self._channelJoined.add(chat.channel)
                
                time.sleep(1 / config.joinPerSecond)
            except:
                utils.logException()
        print('{time} Ending {name}'.format(
            time=datetime.datetime.utcnow(), name=self.__class__.__name__))
    
    def addSocket(self, socketThread):
        self._socketThreads.append(socketThread)
    
    def connected(self, socketThread):
        with self._joinTimesLock:
            self._joinTimes.append(datetime.datetime.utcnow())
    
    def disconnected(self, socketThread):
        with self._channelsLock:
            self._channelJoined -= socketThread.channels.keys()
    
    def part(self, channel):
        with self._channelsLock:
            self._channelJoined.discard(channel)
    
    def recordJoin(self):
        timestamp = datetime.datetime.utcnow()
        with self._joinTimesLock:
            self._joinTimes.append(timestamp)
    
    @staticmethod
    def _getJoinWithLowestPriority(channelsData, notJoinedChannels):
        priority = float(min([float(channelsData[c].joinPriority)
                              for c in notJoinedChannels]))
        return [str(c) for c in notJoinedChannels
                if channelsData[c].joinPriority == priority][0]
