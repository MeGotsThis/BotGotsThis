import socket
import source.ircmessage
import threading
from collections import defaultdict, deque, OrderedDict
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Generic, Iterable, List, NamedTuple
from typing import Optional, Set, Tuple, TypeVar, Union
from source.api.bttv import getBroadcasterEmotes as getBttvEmotes
from source.api.ffz import getBroadcasterEmotes as getFfzEmotes
from .error import ConnectionReset, LoginUnsuccessful
from .. import config, globals, utils
from ..twitchmessage import IrcMessage, IrcMessageParams

socketAlias = socket.socket


ChatMessage = NamedTuple('ChatMessage',
                         [('channel', 'Channel'),
                          ('message', str)])
WhisperMessage = NamedTuple('WhisperMessage',
                            [('nick', str),
                             ('message', str)])


disallowedCommands = {
    '.ignore',
    '/ignore',
    '.disconnect',
    '/disconnect',
    }  # type: Set[str]

_KT = TypeVar('_KT')
_VT = TypeVar('_VT')


class DefaultOrderedDict(OrderedDict, Dict[_KT, _VT], Generic[_KT, _VT]):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self,
                 default_factory: Optional[Callable[[], _VT]]=None,
                 *args,
                 **kwargs) -> None:
        if (default_factory is not None
                and not isinstance(default_factory, Callable)):  # type: ignore --
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *args, **kwargs)
        self.default_factory = default_factory

    def __getitem__(self, key: _KT) -> _VT:
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key: _KT) -> _VT:
        if self.default_factory is None:
            raise KeyError(key)
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
    __slots__ = ['_channel', '_ircChannel', '_socket', '_isMod',
                 '_isSubscriber', '_ircUsers', '_ircOps', '_sessionData',
                 '_joinPriority', '_ffzEmotes', '_ffzCache', '_ffzLock',
                 '_bttvEmotes', '_bttvCache', '_twitchCache', '_bttvLock',
                 '_streamingSince', '_twitchStatus', '_twitchGame',
                 '_serverCheck',
                 ]

    def __init__(self,
                 channel: str,
                 socket: 'Socket',
                 joinPriority: Union[int, float, str]=float('inf')) -> None:
        if not isinstance(channel, str):
            raise TypeError()
        if not isinstance(socket, Socket):
            raise TypeError()
        if not channel:
            raise ValueError()
        self._channel = channel  # type: str
        self._ircChannel = '#' + channel  # type: str
        self._socket = socket  # type: Socket
        self._isMod = False  # type: bool
        self._isSubscriber = False  # type: bool
        self._ircUsers = set()  # type: Set[str]
        self._ircOps = set()  # type: Set[str]
        self._joinPriority = float(joinPriority)  # type: float
        self._sessionData = {}  # type: Dict[Any, Any]
        self._ffzEmotes = {}  # type: Dict[int, str]
        self._ffzCache = datetime.min  # type: datetime
        self._ffzLock = threading.Lock()  # type: threading.Lock
        self._bttvEmotes = {}  # type: Dict[str, str]
        self._bttvCache = datetime.min  # type: datetime
        self._bttvLock = threading.Lock()  # type: threading.Lock
        self._twitchCache = datetime.min  # type: datetime
        self._streamingSince = None  # type: Optional[datetime]
        self._twitchStatus = ''  # type: str
        self._twitchGame = ''  # type: str
        self._serverCheck = datetime.min  # type: datetime

    @property
    def channel(self) -> str:
        return self._channel

    @property
    def ircChannel(self) -> str:
        return self._ircChannel

    @property
    def socket(self) -> 'Socket':
        return self._socket

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
        with self._ffzLock:
            return self._ffzCache

    @property
    def ffzEmotes(self) -> Dict[int, str]:
        return self._ffzEmotes

    @property
    def bttvCache(self) -> datetime:
        with self._bttvLock:
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
    def twitchStatus(self, value: str):
        if value is not None and not isinstance(value, str):
            raise TypeError()
        self._twitchStatus = value

    @property
    def twitchGame(self) -> str:
        return self._twitchGame

    @twitchGame.setter
    def twitchGame(self, value: str):
        if value is not None and not isinstance(value, str):
            raise TypeError()
        self._twitchGame = value

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
        self.socket.partChannel(self)
        self.socket.messaging.clearChat(self)

    def send(self,
             messages: Union[str, Iterable[str]],
             priority: int=1) -> None:
        self.socket.messaging.sendChat(self, messages, priority)

    def clear(self):
        self.socket.messaging.clearChat(self)

    def updateFfzEmotes(self) -> None:
        with self._ffzLock:
            oldTimestamp, self._ffzCache = self._ffzCache, utils.now()
        emotes = getFfzEmotes(self._channel)
        if emotes is not None:
            self._ffzEmotes = emotes
            with self._ffzLock:
                self._ffzCache = utils.now()
        else:
            with self._ffzLock:
                self._ffzCache = oldTimestamp

    def updateBttvEmotes(self) -> None:
        with self._bttvLock:
            oldTimestamp, self._bttvCache = self._bttvCache, utils.now()
        emotes = getBttvEmotes(self._channel)
        if emotes is not None:
            self._bttvEmotes = emotes
            with self._bttvLock:
                self._bttvCache = utils.now()
        else:
            with self._bttvLock:
                self._bttvCache = oldTimestamp


class Socket:
    def __init__(self,
                 name: str,
                 server: str,
                 port: int) -> None:
        self._writeQueue = deque()  # type: deque[Tuple[Tuple[IrcMessage], dict]]
        self._name = name  # type: str
        self._server = server  # type: str
        self._port = port  # type: int
        self._channels = {}  # type: Dict[str, Channel]
        self._channelsLock = threading.Lock()  # type: threading.Lock
        self._socket = None  # type: Optional[socketAlias]
        self._messaging = MessagingQueue()  # type: MessagingQueue
        self.lastSentPing = datetime.max  # type: datetime
        self.lastPing = datetime.max  # type: datetime

    @property
    def name(self) -> str:
        return self._name

    @property
    def server(self) -> str:
        return self._server

    @property
    def port(self) -> int:
        return self._port

    @property
    def address(self) -> Tuple[str, int]:
        return self._server, self._port

    @property
    def socket(self) -> Optional[socketAlias]:
        return self._socket

    @property
    def isConnected(self) -> bool:
        return self._socket is not None

    @property
    def channels(self) -> Dict[str, Channel]:
        with self._channelsLock:
            return self._channels.copy()

    @property
    def messaging(self) -> 'MessagingQueue':
        return self._messaging

    @property
    def writeQueue(self) -> 'deque[Tuple[Tuple[IrcMessage], dict]]':
        return self._writeQueue

    def fileno(self) -> Optional[int]:
        return self._socket and self._socket.fileno()  # type: ignore --

    def connect(self) -> None:
        if self._socket is not None:
            raise ConnectionError('connection already exists')

        connection = socket.socket(socket.AF_INET,
                                   socket.SOCK_STREAM)  # type: socketAlias
        connection.connect(self.address)

        print('{time} {name} Connected {server}'.format(
            time=utils.now(), name=self.name, server=self.server))
        self.login(connection)
        self._socket = connection
        self.lastSentPing = utils.now()
        self.lastPing = utils.now()
        globals.join.connected(self)

    def login(self, connection: socketAlias) -> None:
        if not isinstance(connection, socketAlias):
            raise TypeError()
        commands = [
            IrcMessage(None, None, 'PASS',
                       IrcMessageParams(config.password or None)),
            IrcMessage(None, None, 'NICK', IrcMessageParams(config.botnick)),
            IrcMessage(None, None, 'USER',
                       IrcMessageParams(config.botnick + ' 0 *',
                                        config.botnick)),
            IrcMessage(None, None, 'CAP',
                       IrcMessageParams('REQ', 'twitch.tv/membership')),
            IrcMessage(None, None, 'CAP',
                       IrcMessageParams('REQ', 'twitch.tv/commands')),
            IrcMessage(None, None, 'CAP',
                       IrcMessageParams('REQ', 'twitch.tv/tags')),
        ]  # type: List[IrcMessage]
        for command in commands:  # --type: IrcMessage
            message = (str(command) + '\r\n').encode('utf-8')  # type: bytes
            connection.send(message)
            self._logWrite(command)

    def disconnect(self):
        if self._socket is None:
            raise ConnectionError()
        self._socket.close()
        globals.join.disconnected(self)
        self._socket = None
        self.lastSentPing = datetime.max
        self.lastPing = datetime.max
        print('{time} {name} Disconnected {server}'.format(
            time=utils.now(), name=self.name, server=self._server))

    def write(self,
              command: IrcMessage, *,
              channel: Optional[Channel]=None,
              whisper: Optional[WhisperMessage]=None) -> None:
        if not isinstance(command, IrcMessage):
            raise TypeError()
        if self._socket is None:
            raise ConnectionError()
        try:
            message = str(command) + '\r\n'  # type: str
            messageBytes = message.encode('utf-8')  # type: bytes
            timestamp = utils.now()  # type: datetime
            self._socket.send(messageBytes)
            if command.command == 'PING':
                self.lastSentPing = timestamp
            if command.command == 'JOIN':
                channel.onJoin()
                globals.join.recordJoin()
                print('{time} Joined {channel} on {socket}'.format(
                    time=timestamp, channel=channel.channel, socket=self.name))
            self._logWrite(command, channel=channel, whisper=whisper,
                           timestamp=timestamp)
        except socket.error:
            utils.logException()
            self.disconnect()

    def flushWrite(self) -> None:
        if self._socket is None:
            raise ConnectionError()
        while self.writeQueue:
            item = self.writeQueue.popleft()  # type: Tuple[Tuple[IrcMessage], dict]
            self.write(*item[0], **item[1])  # type: ignore

    def read(self) -> None:
        if self._socket is None:
            raise ConnectionError()
        try:
            ircmsgs = lastRecv = bytes(self._socket.recv(2048))  # type: bytes
            while lastRecv != b'' and lastRecv[-2:] != b'\r\n':
                lastRecv = bytes(self._socket.recv(2048))
                ircmsgs += lastRecv
        except ConnectionError:
            utils.logException()
            self.disconnect()
            return

        try:
            for ircmsg in ircmsgs.split(b'\r\n'):  # --type: bytes
                if not ircmsg:
                    continue
                message = ircmsg.decode('utf-8')  # type: str
                self._logRead(message)
                source.ircmessage.parseMessage(self, message, utils.now())
        except ConnectionReset:
            self.disconnect()
        except LoginUnsuccessful:
            self.disconnect()
            globals.running = False

    def ping(self, message: str = 'ping') -> None:
        self.queueWrite(IrcMessage(None, None, 'PONG',
                                   IrcMessageParams(None, message)),
                        prepend=True)
        self.lastPing = utils.now()

    def sendPing(self) -> None:
        now = utils.now()
        sinceLastSend = now - self.lastSentPing  # type: timedelta
        sinceLast = now - self.lastPing  # type: timedelta
        if sinceLastSend >= timedelta(minutes=1):
            self.queueWrite(IrcMessage(None, None, 'PING',
                                       IrcMessageParams(config.botnick)),
                            prepend=True)
            self.lastSentPing = now
        elif sinceLast >= timedelta(minutes=1, seconds=15):
            self.disconnect()

    def _logRead(self, message: str) -> None:
        file = '{nick}-{server}.log'.format(nick=config.botnick,
                                            server=self.name)  # type: str
        utils.logIrcMessage(file, '< ' + message)

    def _logWrite(self,
                  command: IrcMessage, *,
                  channel: Optional[Channel]=None,
                  whisper: Optional[WhisperMessage]=None,
                  timestamp: Optional[datetime]=None) -> None:
        timestamp = timestamp or utils.now()
        if command.command == 'PASS':
            command = IrcMessage(command='PASS')
        files = []  # type: List[str]
        logs = []  # type: List[str]
        files.append('{bot}-{socket}.log'.format(bot=config.botnick,
                                                 socket=self.name))
        logs.append('> ' + str(command))
        if whisper and channel:
            for file, log in zip(files, logs):  # --type: str, str
                utils.logIrcMessage(file, log, timestamp)
            raise ValueError()
        if whisper:
            files.append('@{nick}@whisper.log'.format(nick=whisper.nick))
            logs.append('{bot}: {message}'.format(bot=config.botnick,
                                                  message=whisper.message))
            files.append('{bot}-All Whisper.log'.format(bot=config.botnick))
            logs.append(
                '{bot} -> {nick}: {message}'.format(
                    bot=config.botnick, nick=whisper.nick,
                    message=whisper.message))
            files.append('{bot}-Raw Whisper.log'.format(bot=config.botnick))
            logs.append('> ' + str(command))
        if channel:
            files.append(
                '{channel}#full.log'.format(channel=channel.ircChannel))
            logs.append('> ' + str(command))
            if command.command == 'PRIVMSG':
                files.append(
                    '{channel}#msg.log'.format(channel=channel.ircChannel))
                logs.append(
                    '{bot}: {message}'.format(bot=config.botnick,
                                              message=command.params.trailing))
        for file, log in zip(files, logs):  # --type: str, str
            utils.logIrcMessage(file, log, timestamp)

    def queueWrite(self,
                   message: IrcMessage, *,
                   channel: Optional[Channel]=None,
                   whisper: Optional[WhisperMessage]=None,
                   prepend: bool=False) -> None:
        if not isinstance(message, IrcMessage):
            raise TypeError()
        kwargs = {}  # type: dict
        if channel:
            if not isinstance(channel, Channel):
                raise TypeError()
            kwargs['channel'] = channel
        if whisper:
            if not isinstance(whisper, WhisperMessage):
                raise TypeError()
            kwargs['whisper'] = whisper
        if channel and whisper:
            raise ValueError()
        item = (message,), kwargs  # type: Tuple[Tuple[IrcMessage], dict]
        if prepend:
            self.writeQueue.appendleft(item)
        else:
            self.writeQueue.append(item)

    def joinChannel(self, channel: Channel) -> None:
        with self._channelsLock:
            self._channels[channel.channel] = channel

    def partChannel(self, channel: Channel) -> None:
        with self._channelsLock:
            if channel.channel not in self._channels:
                return
            self.queueWrite(IrcMessage(None, None, 'PART',
                                       IrcMessageParams(channel.ircChannel)))
            del self._channels[channel.channel]
        globals.join.onPart(channel.channel)
        print('{time} Parted {channel}'.format(
            time=utils.now(), channel=channel.channel))

    def queueMessages(self) -> None:
        self.messaging.cleanOldTimestamps()
        for whisperMessage in iter(self.messaging.popWhisper, None):  # --type: WhisperMessage
            ircMsg = '.w {nick} {message}'.format(
                nick=whisperMessage.nick,
                message=whisperMessage.message)[:config.messageLimit]
            self.queueWrite(
                IrcMessage(None, None, 'PRIVMSG',
                           IrcMessageParams(globals.groupChannel.ircChannel,
                                            ircMsg)),
                whisper=whisperMessage)
        for message in iter(self.messaging.popChat, None):  # --type: ChatMessage
            self.queueWrite(
                IrcMessage(None, None, 'PRIVMSG',
                           IrcMessageParams(
                               message.channel.ircChannel,
                               message.message[:config.messageLimit])),
                channel=message.channel)


class MessagingQueue:
    def __init__(self):
        self._chatQueues = [], [], []  # type: Tuple[List[ChatMessage], ...]
        self._whisperQueue = deque()  # type: deque[WhisperMessage]
        self._queueLock = threading.Lock()  # type: threading.Lock
        self._chatSent = []  # type: List[datetime]
        self._whisperSent = []  # type: List[datetime]
        self._lowQueueRecent = OrderedDict()  # type: OrderedDict[str, Any]
        self._publicTime = defaultdict(
            lambda: datetime.min)  # type: Dict[str, datetime]

    def cleanOldTimestamps(self) -> None:
        timestamp = utils.now()
        msgDuration = timedelta(seconds=config.messageSpan)
        self._chatSent = [t for t in self._chatSent
                          if timestamp - t <= msgDuration]
        msgDuration = timedelta(seconds=config.whiperSpan)
        self._whisperSent = [t for t in self._whisperSent
                             if timestamp - t <= msgDuration]

    def sendChat(self,
                 channel: Channel,
                 messages: Union[str, Iterable[str]],
                 priority: int=1,
                 bypass: bool=False) -> None:
        if not isinstance(channel, Channel):
            raise TypeError()
        listMessages = None  # type: List[str]
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
        whispers = DefaultOrderedDict(list)  # type: DefaultOrderedDict[str, List[str]]
        with self._queueLock:
            for message in listMessages:  # --type: str
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
            for nick in whispers:  # --type; str
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
        with self._queueLock:
            for message in messages:  # --type: str
                self._whisperQueue.append(WhisperMessage(nick, message))

    def popChat(self) -> Optional[ChatMessage]:
        timestamp = utils.now()  # type: datetime
        nextMessage = self._getChatMessage(timestamp)  # type: Optional[ChatMessage]
        if nextMessage:
            self._chatSent.append(timestamp)
        return nextMessage

    def _getChatMessage(self, timestamp: datetime) -> Optional[ChatMessage]:
        publicDelay = timedelta(seconds=config.publicDelay)  # type: timedelta
        isModGood = len(self._chatSent) < config.modLimit  # type: bool
        isModSpamGood = len(self._chatSent) < config.modSpamLimit  # type: bool
        isPublicGood = len(self._chatSent) < config.publicLimit  # type: bool
        with self._queueLock:
            if isPublicGood:
                for queue in self._chatQueues:  # --type: List[ChatMessage]
                    for i, message in enumerate(
                            queue):  # --type: i, ChatMessage
                        last = self._publicTime[message.channel.channel]  # type: datetime
                        if (self._isMod(message.channel)
                            or timestamp - last < publicDelay):
                            continue
                        self._publicTime[message.channel.channel] = timestamp
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
            if isModSpamGood and self._chatQueues[-1]:
                for channel in self._lowQueueRecent:
                    for i, message in enumerate(self._chatQueues[-1]):  # --type: i, ChatMessage
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
        return channel.isMod or config.botnick == channel.channel

    def popWhisper(self) -> Optional[WhisperMessage]:
        if self._whisperQueue and len(self._whisperSent) < config.whiperLimit:
            self._whisperSent.append(utils.now())
            return self._whisperQueue.popleft()
        return None

    def clearChat(self, channel: Channel) -> None:
        with self._queueLock:
            for queue in self._chatQueues:  # --type: List[ChatMessage]
                for message in queue[:]:  # --type: ChatMessage
                    if message.channel.channel == channel.channel:
                        queue.remove(message)

    def clearAllChat(self) -> None:
        with self._queueLock:
            for queue in self._chatQueues:  # --type: List[ChatMessage]
                queue.clear()
