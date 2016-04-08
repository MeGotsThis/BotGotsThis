# Message Queue
from .. import config
from .. import globals
from .. import utils
from ..twitchmessage.ircmessage import IrcMessage
from ..twitchmessage.ircparams import IrcMessageParams
import threading
import traceback
import datetime
import time
import sys

disallowedCommands = (
    '.ignore',
    '/ignore',
    '.disconnect',
    '/disconnect',
    )

class MessageQueue(threading.Thread):
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
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
    
    def queueMessage(self, channelData, message, priority=1, bypass=False):
        if not message:
            return
        if not bypass and message.startswith(disallowedCommands):
            return
        if message.startswith(['/w ', '.w ']):
            msgParts = message.split(' ', 2)
            if len(msgParts) < 3:
                return
            self.queueWhisper(msgParts[1], msgParts[2])
            return
        with self._queueLock:
            param = (channelData, message[:config.messageLimit], None)
            self._queues[priority].append(param)
    
    def queueMultipleMessages(self, channelData, messages, priority=1,
                              bypass=False):
        with self._queueLock:
            for message in messages:
                if not message:
                    continue
                if not bypass and message.startswith(disallowedCommands):
                    continue
                if message.startswith(['/w ', '.w ']):
                    msgParts = message.split(' ', 2)
                    if len(msgParts) < 3:
                        continue
                    param = (globals.groupChannel,
                     '.w ' + msgParts[1] + ' ' + msgParts[2],
                     (msgParts[1].lower(), msgParts[2]))
                else:
                    param = (channelData, message[:config.messageLimit], None)
                self._queues[priority].append(param)
    
    def queueWhisper(self, nick, message, priority=1):
        if not nick and not message:
            return
        with self._queueLock:
            param = (globals.groupChannel,
                     ('.w ' + nick + ' ' + message)[:config.messageLimit],
                     (nick.lower(), message))
            self._queues[priority].append(param)
    
    def run(self):
        print(str(datetime.datetime.utcnow()) + ' Starting MessageQueue')
        try:
            while self.running:
                msg = self._getMessage()
                if msg is not None:
                    if (not msg[0].isMod and config.botnick != msg[0].channel):
                        self._publicTime = datetime.datetime.utcnow()
                    self._timesSent.append(datetime.datetime.utcnow())
                    _ = IrcMessage(command='PRIVMSG',
                                   params=IrcMessageParams(
                                       middle=msg[0].ircChannel,
                                       trailing=msg[1]))
                    try:
                        params = _, msg[0].ircChannel, msg[2]
                        msg[0].socket.sendIrcCommand(*params)
                    except OSError:
                        pass
                time.sleep(1 / config.messagePerSecond)
        except:
            utils.logException()
            raise
        finally:
            for c in globals.clusters.values():
                c.running = False
            globals.join.running = False
            globals.background.running = False
            print(str(datetime.datetime.utcnow()) + ' Ending MessageQueue')
    
    def _getMessage(self):
        msgDuration = datetime.timedelta(seconds=30.1)
        publicDelay = datetime.timedelta(seconds=config.publicDelay)
        botnick = config.botnick
        self._timesSent = [t for t in self._timesSent
                           if datetime.datetime.utcnow() - t <= msgDuration]
        isModGood = int(len(self._timesSent)) < config.modLimit
        isModSpamGood = int(len(self._timesSent)) < config.modSpamLimit
        _ = self._publicTime + publicDelay <= datetime.datetime.utcnow()
        isPublicGood = _ and int(len(self._timesSent)) < config.publicLimit
        
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
        return msgQueue[0].isMod or config.botnick == msgQueue[0].channel
    
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
