from config import config
import threading
import traceback
import datetime
import os.path
import time
import sys

class JoinThread(threading.Thread):
    def __init__(self, *args):
        threading.Thread.__init__(self, *args)
        self._socketThreads = []
        self._joinTimes = []
        self._joinTimesLock = threading.Lock()
        self._channelJoined = set()
        self._channelsLock = threading.Lock()
    
    def run(self):
        print('Starting SocketJoinThread')
        joinDuration = datetime.timedelta(seconds=10.05)
        running = lambda st: st.running
        while any(map(running, self._socketThreads)):
            try:
                utcnow = datetime.datetime.utcnow()
                with self._joinTimesLock:
                    self._joinTimes = [t for t in self._joinTimes
                                       if utcnow - t <= joinDuration]
                    if len(self._joinTimes) >= config.joinLimit:
                        time.sleep(1 / config.joinPerSecond)
                        continue
                
                channels = {}
                for socketThread in self._socketThreads:
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
                    channel = self._getChannelWithLowestPriority(*params)
                    channelData = channels[channel]
                    ircCommand = 'JOIN ' + channelData.channel + '\n'
                    params = ircCommand, channelData.channel
                    channelData.socket.sendIrcCommand(*params)
                    self._channelJoined.add(channelData.channel)
                    with self._joinTimesLock:
                        self._joinTimes.append(datetime.datetime.utcnow())
                    
                    channelData.sendMessage('.mods')
                    
                    print('Joined ' + channelData.channel + ' on ' +
                          channelData.socket.name)
                
                time.sleep(1 / config.joinPerSecond)
            except Exception as e:
                now = datetime.datetime.now()
                exc_type, exc_value, exc_traceback = sys.exc_info()
                _ = traceback.format_exception(
                    exc_type, exc_value, exc_traceback)
                if config.exceptionLog is not None:
                    with open(config.exceptionLog, 'a',
                              encoding='utf-8') as file:
                        file.write(now.strftime('%Y-%m-%d %H:%M:%S.%f '))
                        file.write(' ' + ''.join(_))
        print('Ending SocketJoinThread')
    
    def add(self, socketThread):
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
    
    @staticmethod
    def _getChannelWithLowestPriority(channelsData, notJoinedChannels):
        priority = float(min([float(channelsData[c].joinPriority)
                              for c in notJoinedChannels]))
        return [str(c) for c in notJoinedChannels
                if channelsData[c].joinPriority == priority][0]
