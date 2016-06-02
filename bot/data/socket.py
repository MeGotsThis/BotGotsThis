from .. import config, error, globals, utils
from ..twitchmessage.ircmessage import IrcMessage
from ..twitchmessage.ircparams import IrcMessageParams
from collections import defaultdict, deque, namedtuple, OrderedDict
from collections.abc import Iterable
from datetime import datetime, timedelta
import socket
import source.ircmessage
import threading

ChatMessage = namedtuple('ChatMessage', ['channel', 'message'])
WhisperMessage = namedtuple('WhisperMessage', ['nick', 'whisper'])

disallowedCommands = (
    '.ignore',
    '/ignore',
    '.disconnect',
    '/disconnect',
    )

class Socket:
    def __init__(self, name, server, port):
        # Instance variables for the socket
        self._writeQueue = deque()
        self._name = name
        self._server = server
        self._port = port
        self._channels = {}
        self._channelsLock = threading.Lock()
        self._socket = None
        self.lastSentPing = datetime.max
        self.lastPing = datetime.max
        # Instance variables for the message queuing
        self._chatQueues = [[], [], []]
        self._whisperQueue = deque()
        self._queueLock = threading.Lock()
        self._chatSent = []
        self._whisperSent = []
        self._lowQueueRecent = OrderedDict()
        self._publicTime = defaultdict(lambda: datetime.min)
    
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

    def write(self, command, channel=None, whisper=None):
        if not isinstance(command, IrcMessage):
            raise TypeError()
        if self._socket is None:
            return
        try:
            message = str(command)[:config.messageLimit-2] + '\r\n'
            messageBytes = message.encode('utf-8')
            timestamp = datetime.utcnow()
            self._socket.send(messageBytes)
            if command.command == 'PING':
                self.lastSentPing = datetime.utcnow()
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
            self.queueWrite(IrcMessage(None, None, 'PART',
                                       IrcMessageParams(channel.ircChannel)))
            del self._channels[channel.channel]
        globals.join.part(channel.channel)
        print('{time} Parted {channel}'.format(
            time=datetime.utcnow(), channel=channel.channel))
    
    def processMessages(self):
        msgDuration = timedelta(seconds=30.1)
        self._timesSent = [t for t in self._timesSent
                    if datetime.utcnow() - t <= msgDuration]
        pass
    
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
        if priority < 0 or priority >= len(self._chatQueues):
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
                    for i, message in self._chatQueues[-1]:
                        if message.channel.channel in self._lowQueueRecent:
                            continue
                        if not self._isMod(message.channel):
                            continue
                        del queue[i]
                        self._lowQueueRecent[message.channel.channel] = True
                        return message
            if isModSpamGood:
                for i, message in self._chatQueues[-1]:
                    if message.channel.channel in self._lowQueueRecent:
                        continue
                    if not self._isMod(message.channel):
                        continue
                    del queue[i]
                    self._lowQueueRecent[message.channel.channel] = True
                    return message
        return None
    
    @staticmethod
    def _isMod(channel):
        return channel.isMod or config.botnick == channel.channel
    
    def popWhisper(self):
        if self._whisperQueue and len(self._whisperSent) < config.modLimit:
            self._whisperSent = datetime.utcnow()
            return self._whisperQueue.popleft()
        return None
    
    def clearChat(self, channel):
        with self._queueLock:
            for queue in self._chatQueues:
                for message in queue[:]:
                    if message.channel == channel:
                        queue.remove(message)
    
    def clearAllChat(self, channel):
        with self._queueLock:
            for queue in self._chatQueues:
                queue.clear()
    
    def queueMessages(self):
        for message in iter(self.popWhisper, None):
            self.queueWrite(
                IrcMessage(None, None, 'PRIVMSG',
                           IrcMessageParams(
                               globals.groupChannel.ircChannel,
                               '.w {nick} {message}'.format(
                                   nick=message.nick,
                                   message=message.message))),
                None, message)
        for message in iter(self.popChat, None):
            self.queueWrite(
                IrcMessage(None, None, 'PRIVMSG',
                           IrcMessageParams(message.channel.ircChannel,
                                            message.message)),
                message.channel.ircChannel)
