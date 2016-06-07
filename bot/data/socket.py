from .. import config, globals, utils
from ..twitchmessage.ircmessage import IrcMessage
from ..twitchmessage.ircparams import IrcMessageParams
from . import channel
from .error import ConnectionResetException, LoginUnsuccessfulException
from .message import ChatMessage, MessagingQueue, WhisperMessage
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import socket
import source.ircmessage
import threading

socketAlias = socket.socket

class Socket:
    def __init__(self,
                 name:str,
                 server:str,
                 port:int) -> None:
        self._writeQueue = deque()  # type: deque[Tuple[Tuple[IrcMessage], dict]]
        self._name = name  # type: str
        self._server = server  # type: str
        self._port = port  # type: int
        self._channels = {}  # type: Dict[str, 'channel.Channel']
        self._channelsLock = threading.Lock() # type: threading.Lock
        self._socket = None  # type: Optional[socketAlias]
        self._messaging = MessagingQueue()  # type: MessagingQueue
        self.lastSentPing = datetime.max  # type: datetime
        self.lastPing = datetime.max  # type: datetime
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def socket(self) -> Optional[socketAlias]:
        return self._socket
    
    @property
    def isConnected(self) -> bool:
        return self._socket is not None
    
    @property
    def channels(self) -> Dict[str, 'channel.Channel']:
        with self._channelsLock:
            return self._channels.copy()
    
    @property
    def messaging(self) -> MessagingQueue:
        return self._messaging
    
    @property
    def writeQueue(self) -> deque[Tuple[Tuple[IrcMessage], dict]]:
        return self._writeQueue
    
    def connect(self) -> None:
        if self._socket is not None:
            raise ConnectionError('connection already exists')
        
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # type: socketAlias
        connection.connect((self._server, self._port))
        
        print('{time} {name} Connected {server}'.format(
            time=datetime.utcnow(), name=self.name, server=self._server))
        commands = [
            IrcMessage(None, None, 'PASS', IrcMessageParams(config.password)),
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
        self._socket = connection
        self.lastSentPing = datetime.utcnow()
        self.lastPing = datetime.utcnow()
        globals.join.connected(self)

    def disconnect(self):
        if self._socket is None:
            return
        self._socket.close()
        globals.join.disconnected(self)
        self._socket = None
        self.lastSentPing = datetime.max
        self.lastPing = datetime.max
        print('{time} {name} Disconnected {server}'.format(
            time=datetime.utcnow(), name=self.name, server=self._server))
    
    def fileno(self) -> Optional[int]:
        return self._socket and self._socket.fileno()  # type: ignore

    def write(self,
              command:IrcMessage, *,
              channel:'channel.Channel'=None,
              whisper:WhisperMessage=None) -> None:
        if not isinstance(command, IrcMessage):
            raise TypeError()
        if self._socket is None:
            return
        try:
            message = str(command) + '\r\n'  # type: str
            messageBytes = message.encode('utf-8')  # type: bytes
            timestamp = datetime.utcnow()  # type: datetime
            self._socket.send(messageBytes)
            if command.command == 'PING':
                self.lastSentPing = datetime.utcnow()
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
        while self.writeQueue:
            item = self.writeQueue.popleft()  # type: Tuple[Tuple[IrcMessage], dict]
            self.write(*item[0], **item[1])  # type: ignore
    
    def read(self) -> None:
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
                source.ircmessage.parseMessage(self, message, datetime.utcnow())
        except ConnectionResetException:
            self.disconnect()
        except LoginUnsuccessfulException:
            self.disconnect()
            globals.running = False
    
    def ping(self, message:str='ping') -> None:
        self.queueWrite(IrcMessage(None, None, 'PONG',
                                   IrcMessageParams(None, message)),
                        prepend=True)
        self.lastPing = datetime.utcnow()

    def sendPing(self) -> None:
        sinceLastSend = datetime.utcnow() - self.lastSentPing  # type: timedelta
        sinceLast = datetime.utcnow() - self.lastPing  # type: timedelta
        if sinceLastSend >= timedelta(minutes=1):
            self.queueWrite(IrcMessage(None, None, 'PING',
                                       IrcMessageParams(config.botnick)),
                            prepend=True)
            self.lastSentPing = datetime.utcnow()
        elif sinceLast >= timedelta(minutes=1, seconds=15):
            self.disconnect()
    
    def _logRead(self, message:str) -> None:
        file = '{nick}-{server}.log'.format(nick=config.botnick,
                                            server=self.name)  # type: str
        utils.logIrcMessage(file, '< ' + message)
    
    def _logWrite(self,
                  command:IrcMessage, *,
                  channel:'channel.Channel'=None,
                  whisper:WhisperMessage=None,
                  timestamp:Optional[datetime]=None) -> None:
        timestamp = timestamp or datetime.utcnow()
        if command.command == 'PASS':
            command = IrcMessage(command='PASS')
        files = []  # type: List[str]
        logs = []  # type: List[str]
        files.append('{bot}-{socket}.log'.format(bot=config.botnick,
                                                 socket=self.name))
        logs.append('> ' + str(command))
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
        elif channel:
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
                   command:IrcMessage, *,
                   channel:'channel.Channel'=None,
                   whisper:WhisperMessage=None,
                   prepend:bool=False) -> None:
        if not isinstance(command, IrcMessage):
            raise TypeError()
        kwargs = {}  # type: dict
        if channel:
            kwargs['channel'] = channel
        if whisper:
            kwargs['whisper'] = whisper
        item = (command,), kwargs
        if prepend:
            self.writeQueue.appendleft(item)
        else:
            self.writeQueue.append(item)
    
    def joinChannel(self, channel:'channel.Channel') -> None:
        with self._channelsLock:
            self._channels[channel.channel] = channel
    
    def partChannel(self, channel:'channel.Channel') -> None:
        with self._channelsLock:
            self.queueWrite(IrcMessage(None, None, 'PART',
                                       IrcMessageParams(channel.ircChannel)))
            del self._channels[channel.channel]
        globals.join.part(channel.channel)
        print('{time} Parted {channel}'.format(
            time=datetime.utcnow(), channel=channel.channel))
    
    def queueMessages(self) -> None:
        self.messaging.cleanOldTimestamps()
        for message in iter(self.messaging.popWhisper, None): # --type: WhisperMessage
            self.queueWrite(
                IrcMessage(
                    None, None, 'PRIVMSG',
                    IrcMessageParams(
                        globals.groupChannel.ircChannel,
                        '.w {nick} {message}'.format(
                            nick=message.nick,
                            message=message.message)[:config.messageLimit])),
                whisper=message)
        for message in iter(self.messaging.popChat, None): # --type: ChatMessage
            self.queueWrite(
                IrcMessage(None, None, 'PRIVMSG',
                           IrcMessageParams(
                               message.channel.ircChannel,
                               message.message[:config.messageLimit])),
                channel=message.channel)
