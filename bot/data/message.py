from . import channel
from .. import config
from collections import defaultdict, deque, OrderedDict
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, MutableSequence, NamedTuple, Tuple, Union
import threading

ChatMessage = NamedTuple('ChatMessage',
                         [('channel', 'channel.Channel'), ('message', str)])
WhisperMessage = NamedTuple('WhisperMessage',
                            [('nick', str), ('message', str)])

disallowedCommands = {
    '.ignore',
    '/ignore',
    '.disconnect',
    '/disconnect',
    }  # type: Set[str]


class MessagingQueue:
    def __init__(self) -> None:
        self._chatQueues = [], [], []  # type: Tuple[List[ChatMessage], ...]
        self._whisperQueue = deque()  # type: MutableSequence[WhisperMessage]
        self._queueLock = threading.Lock()  # type: threading.Lock
        self._chatSent = []  # type: List[datetime]
        self._whisperSent = []  # type: List[datetime]
        self._lowQueueRecent = OrderedDict()  # type: Dict[str, Any]
        self._publicTime = defaultdict(lambda: datetime.min)  # type: Dict[str, datetime]

    def cleanOldTimestamps(self) -> None:
        msgDuration = timedelta(seconds=30.1)
        timestamp = datetime.utcnow()
        self._chatSent = [t for t in self._chatSent
                          if timestamp - t <= msgDuration]
        self._whisperSent = [t for t in self._whisperSent
                             if timestamp - t <= msgDuration]
    
    def sendChat(self,
                 channel: 'channel.Channel',
                 messages: Union[str,Iterable[str]],
                 priority: int=1,
                 bypass: bool=False) -> None:
        if isinstance(messages, str):
            messages = messages,
        elif not isinstance(messages, Iterable):
            raise TypeError()
        if (priority < -len(self._chatQueues)
                or priority >= len(self._chatQueues)):
            raise ValueError()
        whispers = defaultdict(list)  # type: defaultdict
        with self._queueLock:
            for message in messages:  # --type: str
                if not message:
                    continue
                if (not bypass
                        and message.startswith(tuple(disallowedCommands))):
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
            for nick in whispers: # --type; str
                self.sendWhisper(nick, whispers[nick])
    
    def sendWhisper(self,
                    nick: str,
                    messages: Union[str,Iterable[str]]) -> None:
        if isinstance(messages, str):
            messages = messages,
        elif not isinstance(messages, Iterable):
            raise TypeError()
        with self._queueLock:
            for message in messages:  # --type: str
                self._whisperQueue.append(WhisperMessage(nick, message))
    
    def popChat(self) -> ChatMessage:
        timestamp = datetime.utcnow()  # type: datetime
        nextMessage = self._getChatMessage(timestamp)  # type: ChatMessage
        if nextMessage:
            self._chatSent.append(timestamp)
        return nextMessage
    
    def _getChatMessage(self, timestamp: datetime) -> ChatMessage:
        publicDelay = timedelta(seconds=config.publicDelay)  # type: timedelta
        isModGood = len(self._chatSent) < config.modLimit  # type: bool
        isModSpamGood = len(self._chatSent) < config.modSpamLimit  # type: bool
        isPublicGood = len(self._chatSent) < config.publicLimit  # type: bool
        with self._queueLock:
            if isPublicGood:
                for queue in self._chatQueues:  # --type: List[ChatMessage]
                    for i, message in enumerate(queue):  # --type: i, ChatMessage
                        last = self._publicTime[message.channel.channel]  # type: datetime
                        if (self._isMod(message.channel)
                                or timestamp - last < publicDelay):
                            continue
                        del queue[i]
                        return message
            if isModGood:
                for queue in self._chatQueues[:-1]:  # --type: List[ChatMessage]
                    for i, message in enumerate(queue):  # --type: i, ChatMessage
                        if not self._isMod(message.channel):
                            continue
                        del queue[i]
                        return message
                else:
                    for i, message in enumerate(self._chatQueues[-1]):  # --type: i, ChatMessage
                        if message.channel.channel in self._lowQueueRecent:
                            continue
                        if not self._isMod(message.channel):
                            continue
                        del self._chatQueues[-1][i]
                        self._lowQueueRecent[message.channel.channel] = True
                        return message
            if isModSpamGood:
                for i, message in enumerate(self._chatQueues[-1]):  # --type: i, ChatMessage
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
    def _isMod(channel: 'channel.Channel') -> bool:
        return channel.isMod or config.botnick == channel.channel
    
    def popWhisper(self):
        if self._whisperQueue and len(self._whisperSent) < config.modLimit:
            self._whisperSent.append(datetime.utcnow())
            return self._whisperQueue.popleft()
        return None
    
    def clearChat(self, channel: 'channel.Channel') -> None:
        with self._queueLock:
            for queue in self._chatQueues:  # --type: List[ChatMessage]
                for message in queue[:]:  # --type: ChatMessage
                    if message.channel.channel == channel.channel:
                        queue.remove(message)
    
    def clearAllChat(self) -> None:
        with self._queueLock:
            for queue in self._chatQueues:  # --type: List[ChatMessage]
                queue.clear()
