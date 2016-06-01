from .. import config, error, globals, utils
from ..twitchmessage.ircmessage import IrcMessage
from ..twitchmessage.ircparams import IrcMessageParams
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
        self._isConnected = False
        self._socket = None
    
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
            IrcMessage(command='PASS',
                       params=IrcMessageParams(middle=config.password)),
            IrcMessage(command='NICK',
                       params=IrcMessageParams(middle=config.botnick)),
            IrcMessage(command='USER',
                       params=IrcMessageParams(
                           middle=config.botnick + ' 0 *',
                           trailing=config.botnick)),
            IrcMessage(command='CAP',
                       params=IrcMessageParams(
                           middle='REQ', trailing='twitch.tv/membership')),
            IrcMessage(command='CAP',
                       params=IrcMessageParams(
                           middle='REQ', trailing='twitch.tv/commands')),
            IrcMessage(command='CAP',
                       params=IrcMessageParams(
                           middle='REQ', trailing='twitch.tv/tags')),
                 ]
        for command in commands:
            message = (str(command) + '\r\n').encode('utf-8')
            connection.send(message)
            self._logWrite(command)
        self._socket = connection
        self.lastSentPing = datetime.utcnow()
        self.lastPing = datetime.utcnow()

    def disconnect(self):
        if self._socket is None:
            return
        self._socket.close()
        globals.join.disconnected(self)
        self._socket = None
        print('{time} {name} Disconnected {server}'.format(
            time=datetime.utcnow(), name=self.name, server=self._server))
    
    def fileno(self):
        return self._socket and self._socket.fileno()

    def write(self, command, channel=None, whisper=None):
        if not isinstance(command, IrcMessage):
            raise TypeError()
        if self._socket is None:
            return
        try:
            message = (str(command) + '\r\n').encode('utf-8')
            timestamp = datetime.utcnow()
            self._socket.send(message)
            if command.command == 'PING':
                self.lastSentPing = datetime.now()
            if command.command == 'JOIN':
                globals.channels[channel[1:]].onJoin()
                globals.join.recordJoin()
                print('{time} Joined {channel} on {socket}'.format(
                    time=timestamp, channel=channel[1:], socket=self.name))
            self._logWrite(command, channel, whisper, timestamp)
        except socket.error:
            utils.logException()
            self.disconnect()
    
    def flushWrite(self):
        while self.writeQueue:
            self.write(*self.writeQueue.popleft())
    
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
                timestamp = datetime.utcnow()
                source.ircmessage.parseMessage(self, ircmsg, timestamp)
        except error.LoginUnsuccessfulException:
            self.disconnect()
            globals.running = False
    
    def ping(self, message='ping'):
        self.queueWrite(
            IrcMessage(command='PONG',
                       params=IrcMessageParams(trailing=message)),
            prepend=True)
        self.lastPing = datetime.utcnow()

    def sendPing(self):
        sinceLastSend = datetime.utcnow() - self.lastSentPing
        sinceLast = datetime.utcnow() - self.lastPing
        if sinceLastSend >= timedelta(minutes=1):
            self.queueWrite(
                IrcMessage(command='PING',
                            params=IrcMessageParams(
                                middle=config.botnick)),
                prepend=True)
            self.lastSentPing = datetime.now()
        elif sinceLast >= timedelta(minutes=1,seconds=15):
            self.disconnect()
    
    def _logRead(self, message):
        file = '{nick}-{server}.log'.format(nick=config.botnick,
                                            server=self.name)
        utils.logIrcMessage(file, '< ' + message)
    
    def _logWrite(self, command, channel=None, whisper=None, timestamp=None):
        timestamp = timestamp or datetime.utcnow()
        if command.command == 'PASS':
            command = IrcMessage(command='PASS')
        file = config.botnick + '-' + self.name + '.log'
        utils.logIrcMessage(file, '> ' + str(command), timestamp)
        if whisper:
            file = '@' + whisper[0] + '@whisper.log'
            log = config.botnick + ': ' + whisper[1]
            utils.logIrcMessage(file, log, timestamp)
            file = config.botnick + '-All Whisper.log'
            log = config.botnick + ' -> ' +  whisper[0] + ': ' + whisper[1]
            utils.logIrcMessage(file, log, timestamp)
            file = config.botnick + '-Raw Whisper.log'
            utils.logIrcMessage(file, '> ' + str(command), timestamp)
        elif channel:
            file = channel + '#full.log'
            utils.logIrcMessage(file, '> ' + str(command), timestamp)
            if command.command == 'PRIVMSG':
                file = channel + '#msg.log'
                log = config.botnick + ': ' + command.params.trailing
                utils.logIrcMessage(file, log, timestamp)
    
    def queueWrite(self, command, channel=None, whisper=None, prepend=False):
        if not isinstance(command, IrcMessage):
            raise TypeError()
        if prepend:
            self._writeQueue.appendleft((command, channel, whisper))
        else:
            self._writeQueue.append((command, channel, whisper))
    
    def joinChannel(self, channel):
        with self._channelsLock:
            self._channels[channel.channel] = channel
    
    def partChannel(self, channel):
        with self._channelsLock:
            self.queueWrite(
                IrcMessage(command='PART',
                           params=IrcMessageParams(
                               middle=channel.ircChannel)))
            del self._channels[channel.channel]
        globals.join.part(channel.channel)
        print('{time} Parted {channel}'.format(
            time=datetime.utcnow(), channel=channel.channel))
