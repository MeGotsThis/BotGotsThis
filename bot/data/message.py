from .. import config
from collections import defaultdict, deque, namedtuple, OrderedDict
from collections.abc import Iterable
from datetime import datetime, timedelta
import threading

ChatMessage = namedtuple('ChatMessage', ['channel', 'message'])
WhisperMessage = namedtuple('WhisperMessage', ['nick', 'message'])

disallowedCommands = (
    '.ignore',
    '/ignore',
    '.disconnect',
    '/disconnect',
    )


class MessagingQueue:
    def __init__(self):
        self._chatQueues = [[], [], []]
        self._whisperQueue = deque()
        self._queueLock = threading.Lock()
        self._chatSent = []
        self._whisperSent = []
        self._lowQueueRecent = OrderedDict()
        self._publicTime = defaultdict(lambda: datetime.min)

    def cleanOldTimestamps(self):
        msgDuration = timedelta(seconds=30.1)
        self._chatSent = [t for t in self._chatSent
                          if datetime.utcnow() - t <= msgDuration]
        self._whisperSent = [t for t in self._whisperSent
                             if datetime.utcnow() - t <= msgDuration]
    
    def cleanTimes(self):
        msgDuration = timedelta(seconds=30.1)
        self._chatSent = [t for t in self._chatSent
                          if datetime.utcnow() - t <= msgDuration]
        self._whisperSent = [t for t in self._whisperSent
                             if datetime.utcnow() - t <= msgDuration]
    
    def sendChat(self, channel, messages, priority=1, bypass=False):
        if isinstance(messages, str):
            messages = messages,
        elif not isinstance(messages, Iterable):
            raise TypeError()
        if (priority < -len(self._chatQueues)
                or priority >= len(self._chatQueues)):
            raise ValueError()
        whispers = defaultdict(list)
        with self._queueLock:
            for message in messages:
                if not message:
                    continue
                if not bypass and message.startswith(disallowedCommands):
                    continue
                if message.startswith(('/w ', '.w ')):
                    tokens = message.split(' ', 2)
                    if len(tokens) < 3:
                        continue
                    whispers[tokens[1].lower()].append((tokens[2], priority))
                else:
                    self._chatQueues[priority].append(
                        ChatMessage(channel, message))
        if whispers:
            for nick in whispers:
                self.sendWhisper(nick, *whispers[nick])
    
    def sendWhisper(self, nick, messages, priority=1):
        if isinstance(messages, str):
            messages = messages,
        elif not isinstance(messages, Iterable):
            raise TypeError()
        with self._queueLock:
            for message in messages:
                self._whisperQueue.append(WhisperMessage(nick, message))
    
    def popChat(self):
        timestamp = datetime.utcnow()
        nextMessage = self._getChatMessage(timestamp)
        if nextMessage:
            self._chatSent.append(timestamp)
        return nextMessage
    
    def _getChatMessage(self, timestamp):
        publicDelay = timedelta(seconds=config.publicDelay)
        isModGood = len(self._chatSent) < config.modLimit
        isModSpamGood = len(self._chatSent) < config.modSpamLimit
        isPublicGood = len(self._chatSent) < config.publicLimit
        with self._queueLock:
            if isPublicGood:
                for queue in self._chatQueues:
                    for i, message in enumerate(queue):
                        last = self._publicTime[message.channel.channel]
                        if (self._isMod(message.channel)
                                or timestamp - last < publicDelay):
                            continue
                        del queue[i]
                        return message
            if isModGood:
                for queue in self._chatQueues[:-1]:
                    for i, message in enumerate(queue):
                        if not self._isMod(message.channel):
                            continue
                        del queue[i]
                        return message
                else:
                    for i, message in enumerate(self._chatQueues[-1]):
                        if message.channel.channel in self._lowQueueRecent:
                            continue
                        if not self._isMod(message.channel):
                            continue
                        del self._chatQueues[-1][i]
                        self._lowQueueRecent[message.channel.channel] = True
                        return message
            if isModSpamGood:
                for i, message in enumerate(self._chatQueues[-1]):
                    if message.channel.channel not in self._lowQueueRecent:
                        continue
                    if not self._isMod(message.channel):
                        continue
                    del self._lowQueueRecent[message.channel.channel]
                    del self._chatQueues[-1][i]
                    self._lowQueueRecent[message.channel.channel] = True
                    return message
        return None
    
    @staticmethod
    def _isMod(channel):
        return channel.isMod or config.botnick == channel.channel
    
    def popWhisper(self):
        if self._whisperQueue and len(self._whisperSent) < config.modLimit:
            self._whisperSent.append(datetime.utcnow())
            return self._whisperQueue.popleft()
        return None
    
    def clearChat(self, channel):
        with self._queueLock:
            for queue in self._chatQueues:
                for message in queue[:]:
                    if message.channel == channel:
                        queue.remove(message)
    
    def clearAllChat(self):
        with self._queueLock:
            for queue in self._chatQueues:
                queue.clear()
