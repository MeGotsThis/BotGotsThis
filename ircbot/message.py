# Message Queue
from config import config
import ircbot.irc
import threading
import traceback
import datetime
import time
import sys

class MessageQueue(threading.Thread):
    def __init__(self, *args):
        threading.Thread.__init__(self, *args)
        self._queues = [[], [], []]
        self._lowQueueRecent = []
        self._timesSent = []
        self._publicTime = datetime.datetime.min
        self._queueLock = threading.Lock()
        self._running = True
    
    @property
    def running(self):
        return self._running
    
    @running.setter
    def running(self, value):
        self._running = value
    
    def queueMessage(self, channelData, message, priority):
        with self._queueLock:
            self._queues[priority].append((channelData, message))
    
    def queueMultipleMessages(self, channelData, messages, priority):
        with self._queueLock:
            for message in messages:
                self._queues[priority].append((channelData, message))
    
    def run(self):
        print('Starting MessageQueue')
        try:
            while self.running:
                msg = self._getMessage()
                if msg is not None:
                    if (config.botnick not in msg[0].mods and
                        '#' + config.botnick != msg[0].channel):
                        self._publicTime = datetime.datetime.utcnow()
                    self._timesSent.append(datetime.datetime.utcnow())
                    _ = 'PRIVMSG ' + msg[0].channel + ' :' + msg[1] + '\n'
                    try:
                        msg[0].socket.sendIrcCommand(_, msg[0].channel)
                    except OSError:
                        pass
                time.sleep(1 / config.messagePerSecond)
        except Exception as e:
            now = datetime.datetime.now()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            _ = traceback.format_exception(exc_type, exc_value, exc_traceback)
            if config.exceptionLog is not None:
                with open(config.exceptionLog, 'a', encoding='utf-8') as file:
                    file.write(now.strftime('%Y-%m-%d %H:%M:%S.%f '))
                    file.write(' ' + ''.join(_))
            ircbot.irc.socket.running = False
            raise
        finally:
            print('Ending MessageQueue')
    
    def _getMessage(self):
        msgDuration = datetime.timedelta(seconds=30.1)
        publicDelay = datetime.timedelta(seconds=config.publicDelay)
        botnick = config.botnick
        self._timesSent = [t for t in self._timesSent
                           if datetime.datetime.utcnow() - t <= msgDuration]
        isModGood = len(self._timesSent) < config.modLimit
        isModSpamGood = len(self._timesSent) < config.modSpamLimit
        _ = self._publicTime + publicDelay <= datetime.datetime.utcnow()
        isPublicGood = _ and len(self._timesSent) < config.publicLimit
        
        msg = None
        with self._queueLock:
            if isPublicGood:
                for j in [0, 1, 2]:
                    if msg is not None:
                        continue
                    queue = self._queues[j]
                    condition = lambda i: (
                        not self._isModInChannel(queue[i]) and
                        queue[i][0].socket.isConnected)
                    msg = self._selectMsg(queue, condition)
            if isModGood:
                for j in [0, 1]:
                    if msg is not None:
                        continue
                    queue = self._queues[j]
                    condition = lambda i: (
                        self._isModInChannel(queue[i]) and
                        queue[i][0].socket.isConnected)
                    msg = self._selectMsg(queue, condition)
                if msg is None:
                    queue = self._queues[2]
                    condition = lambda i: (
                        queue[i][0].channel not in self._lowQueueRecent and
                        self._isModInChannel(queue[i]) and
                        queue[i][0].socket.isConnected)
                    msg = self._selectMsg(queue, condition)
                    if msg is not None:
                        self._lowQueueRecent.append(msg[0].channel)
            if isModSpamGood:
                if msg is None:
                    queue = self._queues[2]
                    for channel in self._lowQueueRecent:
                        condition = lambda i: (
                            queue[i][0].channel == channel and
                            self._isModInChannel(queue[i]) and
                            queue[i][0].socket.isConnected)
                        msg = self._selectMsg(queue, condition)
                        if msg is not None:
                            self._lowQueueRecent.remove(msg[0].channel)
                            self._lowQueueRecent.append(msg[0].channel)
                            break
                if msg is None:
                    if len(self._queues[2]) == 0:
                        self._lowQueueRecent.clear()
        return msg
    
    @staticmethod
    def _selectMsg(queue, condition):
        for i in range(len(queue)):
            if condition(i):
                msg = queue[i]
                del queue[i]
                return msg
        return None
    
    @staticmethod
    def _isModInChannel(msgQueue):
        isMod = config.botnick in msgQueue[0].mods
        isMod = isMod or '#' + config.botnick == msgQueue[0].channel
        return isMod
    
    def clearQueue(self, channel):
        with self._queueLock:
            for j in [0, 1, 2]:
                queue = self._queues[j]
                for msg in queue[:]:
                    if msg[0].channel == channel:
                        queue.remove(msg)
    
    def clearAllQueue(self):
        with self._queueLock:
            for j in [0, 1, 2]:
                self._queues[j].clear()
