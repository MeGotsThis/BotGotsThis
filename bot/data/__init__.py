import bot
from bot.coroutine import connection as connectionM
from collections import defaultdict, deque, OrderedDict
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Generic, Iterable, List, NamedTuple  # noqa: F401, E501
from typing import Optional, Set, Tuple, TypeVar, Union  # noqa: F401
from source.api import bttv, ffz
from .. import utils


class ChatMessage(NamedTuple):
    channel: 'Channel'
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

_KT = TypeVar('_KT')
_VT = TypeVar('_VT')


class DefaultOrderedDict(OrderedDict, Dict[_KT, _VT], Generic[_KT, _VT]):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self,
                 default_factory: Optional[Callable[[], _VT]]=None,
                 *args,
                 **kwargs) -> None:
        if default_factory is not None:
            if not callable(default_factory):
                raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *args, **kwargs)
        self.default_factory: Optional[Callable[[], _VT]] = default_factory

    def __getitem__(self, key: _KT) -> _VT:
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key: _KT) -> _VT:
        if self.default_factory is None:
            raise KeyError(key)
        value: _VT
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self) -> 'DefaultOrderedDict[_KT, _VT]':
        return self.__copy__()

    def __copy__(self) -> 'DefaultOrderedDict[_KT, _VT]':
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo: Any) -> 'DefaultOrderedDict[_KT, _VT]':
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))

    def __repr__(self) -> str:
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                               OrderedDict.__repr__(self))


class Channel:
    __slots__ = ['_channel', '_ircChannel', '_connection', '_isMod',
                 '_isSubscriber', '_ircUsers', '_ircOps', '_sessionData',
                 '_joinPriority', '_ffzEmotes', '_ffzCache', '_ffzLock',
                 '_bttvEmotes', '_bttvCache', '_twitchCache', '_bttvLock',
                 '_streamingSince', '_twitchStatus', '_twitchGame',
                 '_community', '_serverCheck',
                 ]

    def __init__(self,
                 channel: str,
                 connection_: 'connectionM.ConnectionHandler',
                 joinPriority: Union[int, float, str]=float('inf')) -> None:
        if not isinstance(channel, str):
            raise TypeError()
        if not isinstance(connection_, connectionM.ConnectionHandler):
            raise TypeError()
        if not channel:
            raise ValueError()
        self._channel: str = channel
        self._ircChannel: str = '#' + channel
        self._connection: connectionM.ConnectionHandler = connection_
        self._isMod: bool = False
        self._isSubscriber: bool = False
        self._ircUsers: Set[str] = set()
        self._ircOps: Set[str] = set()
        self._joinPriority: float = float(joinPriority)
        self._sessionData: Dict[Any, Any] = {}
        self._ffzEmotes: Dict[int, str] = {}
        self._ffzCache: datetime = datetime.min
        self._bttvEmotes: Dict[str, str] = {}
        self._bttvCache: datetime = datetime.min
        self._twitchCache: datetime = datetime.min
        self._streamingSince: Optional[datetime] = None
        self._twitchStatus: Optional[str] = ''
        self._twitchGame: Optional[str] = ''
        self._community: Optional[str] = None
        self._serverCheck: datetime = datetime.min

    @property
    def channel(self) -> str:
        return self._channel

    @property
    def ircChannel(self) -> str:
        return self._ircChannel

    @property
    def connection(self) -> 'connectionM.ConnectionHandler':
        return self._connection

    @property
    def isMod(self) -> bool:
        return self._isMod

    @isMod.setter
    def isMod(self, value: bool) -> None:
        self._isMod = bool(value)

    @property
    def isSubscriber(self) -> bool:
        return self._isSubscriber

    @isSubscriber.setter
    def isSubscriber(self, value: bool) -> None:
        self._isSubscriber = bool(value)

    @property
    def ircUsers(self) -> Set[str]:
        return self._ircUsers

    @property
    def ircOps(self) -> Set[str]:
        return self._ircOps

    @property
    def joinPriority(self) -> float:
        return self._joinPriority

    @joinPriority.setter
    def joinPriority(self, value: Union[int, float, str]) -> None:
        self._joinPriority = float(value)

    @property
    def sessionData(self) -> Dict[Any, Any]:
        return self._sessionData

    @property
    def ffzCache(self) -> datetime:
        return self._ffzCache

    @property
    def ffzEmotes(self) -> Dict[int, str]:
        return self._ffzEmotes

    @property
    def bttvCache(self) -> datetime:
        return self._bttvCache

    @property
    def bttvEmotes(self) -> Dict[str, str]:
        return self._bttvEmotes

    @property
    def streamingSince(self) -> Optional[datetime]:
        return self._streamingSince

    @streamingSince.setter
    def streamingSince(self, value: Optional[datetime]) -> None:
        if value is not None and not isinstance(value, datetime):
            raise TypeError()
        self._streamingSince = value

    @property
    def isStreaming(self) -> bool:
        return self._streamingSince is not None

    @property
    def twitchCache(self) -> datetime:
        return self._twitchCache

    @twitchCache.setter
    def twitchCache(self, value: datetime):
        if not isinstance(value, datetime):
            raise TypeError()
        self._twitchCache = value

    @property
    def twitchStatus(self) -> str:
        return self._twitchStatus

    @twitchStatus.setter
    def twitchStatus(self, value: Optional[str]):
        if value is not None and not isinstance(value, str):
            raise TypeError()
        self._twitchStatus = value

    @property
    def twitchGame(self) -> str:
        return self._twitchGame

    @twitchGame.setter
    def twitchGame(self, value: Optional[str]):
        if value is not None and not isinstance(value, str):
            raise TypeError()
        self._twitchGame = value

    @property
    def community(self) -> str:
        return self._community

    @community.setter
    def community(self, value: Optional[str]):
        if value is not None and not isinstance(value, str):
            raise TypeError()
        self._community = value

    @property
    def serverCheck(self) -> datetime:
        return self._serverCheck

    @serverCheck.setter
    def serverCheck(self, value: datetime):
        if not isinstance(value, datetime):
            raise TypeError()
        self._serverCheck = value

    def onJoin(self) -> None:
        self._ircUsers.clear()
        self._ircOps.clear()

    def part(self) -> None:
        self.connection.part_channel(self)
        self.connection.messaging.clearChat(self)

    def send(self,
             messages: Union[str, Iterable[str]],
             priority: int=1) -> None:
        self.connection.messaging.sendChat(self, messages, priority)

    def clear(self):
        self.connection.messaging.clearChat(self)

    async def updateFfzEmotes(self) -> None:
        oldTimestamp: datetime
        oldTimestamp, self._ffzCache = self._ffzCache, utils.now()
        emotes: Optional[Dict[int, str]]
        emotes = await ffz.getBroadcasterEmotes(self._channel)
        if emotes is not None:
            self._ffzEmotes = emotes
            self._ffzCache = utils.now()
        else:
            self._ffzCache = oldTimestamp

    async def updateBttvEmotes(self) -> None:
        oldTimestamp: datetime
        oldTimestamp, self._bttvCache = self._bttvCache, utils.now()
        emotes: Optional[Dict[str, str]]
        emotes = await bttv.getBroadcasterEmotes(self._channel)
        if emotes is not None:
            self._bttvEmotes = emotes
            self._bttvCache = utils.now()
        else:
            self._bttvCache = oldTimestamp


class MessagingQueue:
    def __init__(self):
        self._chatQueues: Tuple[List[ChatMessage], ...]
        self._chatQueues = [], [], []
        self._whisperQueue: deque[WhisperMessage] = deque()
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
                 channel: Channel,
                 messages: Union[str, Iterable[str]],
                 priority: int=1,
                 bypass: bool=False) -> None:
        if not isinstance(channel, Channel):
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
        whispers: DefaultOrderedDict[str, List[str]]
        whispers = DefaultOrderedDict(list)

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

    def _getChatMessage(self, timestamp: datetime) -> Optional[ChatMessage]:
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
    def _isMod(channel: Channel) -> bool:
        return channel.isMod or bot.config.botnick == channel.channel

    def popWhisper(self) -> Optional[WhisperMessage]:
        if (self._whisperQueue
                and len(self._whisperSent) < bot.config.whiperLimit):
            self._whisperSent.append(utils.now())
            return self._whisperQueue.popleft()
        return None

    def clearChat(self, channel: Channel) -> None:
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
