import bot

from collections import defaultdict, deque, OrderedDict
from datetime import datetime, timedelta
from typing import Any, Deque, Dict, Iterable, NamedTuple, List, Optional, Set  # noqa: F401,E501
from typing import Tuple, Union  # noqa: F401

from bot import utils
from . import _channel, _collections


class ChatMessage(NamedTuple):
    channel: '_channel.Channel'
    message: str


class WhisperMessage(NamedTuple):
    nick: str
    message: str


disallowedCommands: Set[str] = {
    '.ignore',
    '/ignore',
    '.disconnect',
    '/disconnect',
    }


class MessagingQueue:
    def __init__(self) -> None:
        self._chatQueues: Tuple[List[ChatMessage], ...]
        self._chatQueues = [], [], []
        self._whisperQueue: Deque[WhisperMessage] = deque()
        self._chatSent: List[datetime] = []
        self._whisperSent: List[datetime] = []
        self._lowQueueRecent: OrderedDict[str, Any] = OrderedDict()
        self._publicTime: Dict[str, datetime]
        self._publicTime = defaultdict(lambda: datetime.min)

    def cleanOldTimestamps(self) -> None:
        timestamp = utils.now()
        msgDuration = timedelta(seconds=bot.config.messageSpan)
        self._chatSent = [t for t in self._chatSent
                          if timestamp - t <= msgDuration]
        msgDuration = timedelta(seconds=bot.config.whiperSpan)
        self._whisperSent = [t for t in self._whisperSent
                             if timestamp - t <= msgDuration]

    def sendChat(self,
                 channel: '_channel.Channel',
                 messages: Union[str, Iterable[str]],
                 priority: int=1,
                 bypass: bool=False) -> None:
        if not isinstance(channel, _channel.Channel):
            raise TypeError()
        listMessages: List[str]
        if isinstance(messages, str):
            listMessages = [messages]
        elif isinstance(messages, Iterable):
            listMessages = list(messages)
        else:
            raise TypeError()
        if any(msg for msg in listMessages if not isinstance(msg, str)):
            raise TypeError()
        if (priority < -len(self._chatQueues)
                or priority >= len(self._chatQueues)):
            raise ValueError()
        whispers: _collections.DefaultOrderedDict[str, List[str]]
        whispers = _collections.DefaultOrderedDict(list)

        message: str
        for message in listMessages:
            if not message:
                continue
            if (not bypass
                    and message.startswith(tuple(disallowedCommands))):
                continue
            if message.startswith(('/w ', '.w ')):
                tokens = message.split(' ', 2)
                if len(tokens) < 3:
                    continue
                whispers[tokens[1].lower()].append(tokens[2])
            else:
                self._chatQueues[priority].append(
                    ChatMessage(channel, message))
        if whispers:
            for nick in whispers:  # type; str
                self.sendWhisper(nick, whispers[nick])

    def sendWhisper(self,
                    nick: str,
                    messages: Union[str, Iterable[str]]) -> None:
        if not isinstance(nick, str):
            raise TypeError()
        if isinstance(messages, str):
            messages = messages,
        elif not isinstance(messages, Iterable):
            raise TypeError()
        message: str
        for message in messages:
            self._whisperQueue.append(WhisperMessage(nick, message))

    def popChat(self) -> Optional[ChatMessage]:
        timestamp: datetime = utils.now()
        nextMessage:  Optional[ChatMessage] = self._getChatMessage(timestamp)
        if nextMessage:
            self._chatSent.append(timestamp)
        return nextMessage

    def _getChatMessage(self, timestamp: datetime
                        ) -> Optional[ChatMessage]:
        publicDelay: timedelta = timedelta(seconds=bot.config.publicDelay)
        isModGood: bool = len(self._chatSent) < bot.config.modLimit
        isModSpamGood: bool = len(self._chatSent) < bot.config.modSpamLimit
        isPublicGood: bool = len(self._chatSent) < bot.config.publicLimit

        if isPublicGood:
            queue: List[ChatMessage]
            i: int
            message: ChatMessage
            for queue in self._chatQueues:
                for i, message in enumerate(queue):
                    last: datetime
                    last = self._publicTime[message.channel.channel]
                    if (self._isMod(message.channel)
                            or timestamp - last < publicDelay):
                        continue
                    self._publicTime[message.channel.channel] = timestamp
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
        if isModSpamGood and self._chatQueues[-1]:
            for channel in self._lowQueueRecent:
                for i, message in enumerate(self._chatQueues[-1]):
                    if message.channel.channel != channel:
                        continue
                    if not self._isMod(message.channel):
                        continue
                    del self._chatQueues[-1][i]
                    self._lowQueueRecent[message.channel.channel] = True
                    self._lowQueueRecent.move_to_end(message.channel.channel)
                    return message
        return None

    @staticmethod
    def _isMod(channel: '_channel.Channel') -> bool:
        return channel.isMod or bot.config.botnick == channel.channel

    def popWhisper(self) -> Optional[WhisperMessage]:
        if (self._whisperQueue
                and len(self._whisperSent) < bot.config.whiperLimit):
            self._whisperSent.append(utils.now())
            return self._whisperQueue.popleft()
        return None

    def clearChat(self, channel: '_channel.Channel') -> None:
        queue: List[ChatMessage]
        message: ChatMessage
        for queue in self._chatQueues:
            for message in queue[:]:
                if message.channel.channel == channel.channel:
                    queue.remove(message)

    def clearAllChat(self) -> None:
        queue: List[ChatMessage]
        for queue in self._chatQueues:
            queue.clear()
