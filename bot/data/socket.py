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
        self._socket = connection
        print('{time} {name} Connected {server}'.format(
            time=datetime.utcnow(), name=self.name, server=self._server))
        comms = [
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
        for comm in comms:
            if self._socket is None:
                break
            self.write(comm)
        self.lastSentPing = datetime.utcnow()
        self.lastPing = datetime.utcnow()

    def cleanup(self):
        self._socket.close()
        globals.join.disconnected(self)
        self._socket = None
        print('{time} {name} Disconnected {server}'.format(
            time=datetime.utcnow(), name=self.name, server=self._server))
    
    def fileno(self):
        return self._socket.fileno()

    def write(self, command, channel=None, whisper=None):
        if not isinstance(command, IrcMessage):
            raise TypeError()
        try:
            message = (str(command) + '\r\n').encode('utf-8')
            self._socket.send(message)
            if command.command == 'PING':
                self.lastSentPing = datetime.now()
            if command.command == 'join':
                chat.onJoin()
                globals.join.recordJoin()
            self._logWrite(command, channel, whisper)
        except socket.error:
            utils.logException()
            self.cleanup()
    
    def flushWrite(self):
        while self.writeQueue:
            self.write(*self.writeQueue.popleft())
    
    def read(self):
        ircmsgs = lastRecv = bytes(self._socket.recv(2048))
        while lastRecv != b'' and lastRecv[-2:] != b'\r\n':
            lastRecv = bytes(self._socket.recv(2048))
            ircmsgs += lastRecv
        
        for ircmsg in ircmsgs.split(b'\r\n'):
            if not ircmsg:
                continue
            ircmsg = bytes(ircmsg).decode('utf-8')
            self._logRead(ircmsg)
            timestamp = datetime.utcnow()
            source.ircmessage.parseMessage(self, ircmsg, timestamp)
    
    def ping(self):
        sinceLastSend = datetime.utcnow() - self.lastSentPing
        sinceLast = datetime.utcnow() - self.lastPing
        if sinceLastSend >= timedelta(minutes=1):
            self.writeQueue(
                IrcMessage(command='PING',
                            params=IrcMessageParams(
                                middle=config.botnick)),
                prepend=True)
        elif sinceLast >= timedelta(minutes=1,seconds=15):
            raise error.NoPingException()
    
    def _logRead(self, message):
        file = '{nick}-{server}.log'.format(nick=config.botnick,
                                            server=self.name)
        utils.logIrcMessage(file, '< ' + message)
    
    def _logWrite(self, command, channel=None, whisper=None):
        timestamp = datetime.utcnow()
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
