from .. import config, globals, utils
from ..twitchmessage.ircmessage import IrcMessage
from ..twitchmessage.ircparams import IrcMessageParams
from .error import ConnectionResetException, LoginUnsuccessfulException
from .message import MessagingQueue
from collections import deque
from datetime import datetime, timedelta
import socket
import source.ircmessage
import threading

class Socket:
    def __init__(self, name, server, port):
        self._writeQueue = deque()
        self._name = name
        self._server = server
        self._port = port
        self._channels = {}
        self._channelsLock = threading.Lock()
        self._socket = None
        self._messaging = MessagingQueue()
        self.lastSentPing = datetime.max
        self.lastPing = datetime.max
    
    @property
    def name(self):
        return self._name
    
    @property
    def socket(self):
        return self._socket
    
    @property
    def isConnected(self):
        return self._socket is not None
    
    @property
    def channels(self):
        with self._channelsLock:
            return self._channels.copy()
    
    @property
    def messaging(self):
        return self._messaging
    
    @property
    def writeQueue(self):
        return self._writeQueue
    
    def connect(self):
        if self._socket is not None:
            raise ConnectionError('connection already exists')
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect((self._server, self._port))
        except:
            raise
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
            ]
        for command in commands:
            message = (str(command) + '\r\n').encode('utf-8')
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
    
    def fileno(self):
        return self._socket and self._socket.fileno()

    def write(self, command, *, channel=None, whisper=None):
        if not isinstance(command, IrcMessage):
            raise TypeError()
        if self._socket is None:
            return
        try:
            message = str(command) + '\r\n'
            messageBytes = message.encode('utf-8')
            timestamp = datetime.utcnow()
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
    
    def flushWrite(self):
        while self.writeQueue:
            item = self.writeQueue.popleft()
            self.write(*item[0], **item[1])
    
    def read(self):
        ircmsgs = lastRecv = bytes(self._socket.recv(2048))
        while lastRecv != b'' and lastRecv[-2:] != b'\r\n':
            lastRecv = bytes(self._socket.recv(2048))
            ircmsgs += lastRecv
        
        try:
            for ircmsg in ircmsgs.split(b'\r\n'):
                if not ircmsg:
                    continue
                ircmsg = bytes(ircmsg).decode('utf-8')
                self._logRead(ircmsg)
                source.ircmessage.parseMessage(self, ircmsg, datetime.utcnow())
        except ConnectionResetException:
            self.disconnect()
        except LoginUnsuccessfulException:
            self.disconnect()
            globals.running = False
    
    def ping(self, message='ping'):
        self.queueWrite(IrcMessage(None, None, 'PONG',
                                   IrcMessageParams(None, message)),
                        prepend=True)
        self.lastPing = datetime.utcnow()

    def sendPing(self):
        sinceLastSend = datetime.utcnow() - self.lastSentPing
        sinceLast = datetime.utcnow() - self.lastPing
        if sinceLastSend >= timedelta(minutes=1):
            self.queueWrite(IrcMessage(None, None, 'PING',
                                       IrcMessageParams(config.botnick)),
                            prepend=True)
            self.lastSentPing = datetime.utcnow()
        elif sinceLast >= timedelta(minutes=1,seconds=15):
            self.disconnect()
    
    def _logRead(self, message):
        file = '{nick}-{server}.log'.format(nick=config.botnick,
                                            server=self.name)
        utils.logIrcMessage(file, '< ' + message)
    
    def _logWrite(self, command, *,
                  channel=None, whisper=None, timestamp=None):
        timestamp = timestamp or datetime.utcnow()
        if command.command == 'PASS':
            command = IrcMessage(command='PASS')
        files = []
        logs = []
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
        for file, log in zip(files, logs):
            utils.logIrcMessage(file, log, timestamp)
    
    def queueWrite(self, command, *,
                   channel=None, whisper=None, prepend=False):
        if not isinstance(command, IrcMessage):
            raise TypeError()
        kwargs = {}
        if channel:
            kwargs['channel'] = channel
        if whisper:
            kwargs['whisper'] = whisper
        item = (command,), kwargs
        if prepend:
            self.writeQueue.appendleft(item)
        else:
            self.writeQueue.append(item)
    
    def joinChannel(self, channel):
        with self._channelsLock:
            self._channels[channel.channel] = channel
    
    def partChannel(self, channel):
        with self._channelsLock:
            self.queueWrite(IrcMessage(None, None, 'PART',
                                       IrcMessageParams(channel.ircChannel)))
            del self._channels[channel.channel]
        globals.join.part(channel.channel)
        print('{time} Parted {channel}'.format(
            time=datetime.utcnow(), channel=channel.channel))
    
    def queueMessages(self):
        self.messaging.cleanOldTimestamps()
        for message in iter(self.messaging.popWhisper, None):
            self.queueWrite(
                IrcMessage(
                    None, None, 'PRIVMSG',
                    IrcMessageParams(
                        globals.groupChannel.ircChannel,
                        '.w {nick} {message}'.format(
                            nick=message.nick,
                            message=message.message)[:config.messageLimit])),
                whisper=message)
        for message in iter(self.messaging.popChat, None):
            self.queueWrite(
                IrcMessage(None, None, 'PRIVMSG',
                           IrcMessageParams(
                               message.channel.ircChannel,
                               message.message[:config.messageLimit])),
                channel=message.channel)
