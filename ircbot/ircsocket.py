from config import config
from twitchmessage.ircmessage import IrcMessage
from twitchmessage.ircparams import IrcMessageParams
import ircchannel.commands
import ircuser.notice
import ircuser.userstate
import ircbot.irc
import ircwhisper.commands
import threading
import traceback
import datetime
import os.path
import socket
import time
import sys

class SocketThread(threading.Thread):
    def __init__(self, server, **args):
        threading.Thread.__init__(self, **args)
        self._server = server
        self._channels = {}
        self._channelsLock = threading.Lock()
        self._isConnected = False
        self._running = True
    
    @property
    def channels(self):
        with self._channelsLock:
            return self._channels.copy()
    
    @property
    def isConnected(self):
        return self._isConnected
    
    @property
    def running(self):
        return self._running
    
    @running.setter
    def running(self, value):
        self._running = value
    
    def run(self):
        print(str(datetime.datetime.utcnow()) + ' Starting SocketThread ' +
              self.name)
        
        while self.running:
            self._ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._ircsock.settimeout(5)
            try:
                self._connect()
            except socket.error as e:
                print(str(datetime.datetime.utcnow()) + ' ' + self.name + 
                      ' ' + str(e))
                time.sleep(5)
                continue
            self.lastSentPing = datetime.datetime.now()
            self.lastPing = datetime.datetime.now()
            print(str(datetime.datetime.utcnow()) + ' ' + self.name +
                  ' Connected ' + self._server)
            
            ircbot.irc.join.connected(self)
            self._isConnected = True
            try:
                while self.running:
                    try:
                        ircmsgs = lastRecv = bytes(self._ircsock.recv(2048))
                        while lastRecv != b'' and lastRecv[-2:] != b'\r\n':
                            lastRecv = bytes(self._ircsock.recv(2048))
                            ircmsgs += lastRecv
                        
                        for ircmsg in ircmsgs.split(b'\r\n'):
                            if not ircmsg:
                                continue
                            ircmsg = bytes(ircmsg).decode('utf-8')
                            now = datetime.datetime.utcnow()
                            file = config.botnick + '-' + self.name + '.log'
                            _logMessage(file, '< ' + ircmsg)
                            self._parseMsg(ircmsg, now)
                    except socket.timeout:
                        pass
                    sinceLastSend = datetime.datetime.now() - self.lastSentPing
                    sinceLast = datetime.datetime.now() - self.lastPing
                    if sinceLastSend >= datetime.timedelta(minutes=1):
                        self.sendIrcCommand(
                            IrcMessage(command='PING',
                                       params=IrcMessageParams(
                                           middle=config.botnick)))
                        self.lastSentPing = datetime.datetime.now()
                    elif sinceLast >= datetime.timedelta(minutes=1,seconds=15):
                        raise NoPingException()
            except NoPingException:
                pass
            except LoginUnsuccessfulException:
                pass
            except:
                ircbot.irc.logException()
            finally:
                self._ircsock.close()
            self._isConnected = False
            ircbot.irc.join.disconnected(self)
            print(str(datetime.datetime.utcnow()) + ' ' +  self.name +
                  ' Disconnected ' + self._server)
            time.sleep(5)
        print(str(datetime.datetime.utcnow()) + ' Ending SocketThread ' +
              self.name)
    
    def sendIrcCommand(self, message, channel=None, whisper=None):
        if isinstance(message, IrcMessage):
            pass
        else:
            raise TypeError()
        command = (str(message) + '\r\n').encode('utf-8')
        try:
            self._ircsock.send(command)
        except socket.error:
            extra = 'Command: ' + str(message)
            if channel:
                extra = 'Channel: ' + channel + '\n' + extra
            ircbot.irc.logException(extra)
            self._isConnected = False
        
        now = datetime.datetime.utcnow()
        if message.command == 'PASS':
            message = IrcMessage(command='PASS')
        file = config.botnick + '-' + self.name + '.log'
        _logMessage(file, '> ' + str(message), now)
        if whisper:
            file = '@' + whisper[0] + '@whisper.log'
            _logMessage(file, config.botnick + ': ' + whisper[1], now)
            file = config.botnick + '-All Whisper.log'
            log = config.botnick + ' -> ' +  whisper[0] + ': ' + whisper[1]
            _logMessage(file, log, now)
            file = config.botnick + '-Raw Whisper.log'
            _logMessage(file, '> ' + str(message), now)
        elif channel:
            file = channel + '#full.log'
            _logMessage(file, '> ' + str(message), now)
            if message.command == 'PRIVMSG':
                file = channel + '#msg.log'
                log = config.botnick + ': ' + message.params.trailing
                _logMessage(file, log, now)
    
    def _connect(self):
        self._ircsock.connect((self._server, 6667))
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
            self.sendIrcCommand(comm)
    
    def joinChannel(self, channelData):
        with self._channelsLock:
            self._channels[channelData.channel] = channelData
    
    def partChannel(self, channelData):
        with self._channelsLock:
            self.sendIrcCommand(
                IrcMessage(command='PART',
                           params=IrcMessageParams(
                               middle=channelData.channel)))
            del self._channels[channelData.channel]
        ircbot.irc.join.part(channelData.channel)
        print(str(datetime.datetime.utcnow()) + ' Parted ' +
              channelData.channel)
    
    def ping(self, message='ping'):
        self.sendIrcCommand(
            IrcMessage(command='PONG',
                       params=IrcMessageParams(trailing=message)))
        self.lastPing = datetime.datetime.now()

    def _parseMsg(self, ircmsg, now):
        message = IrcMessage(message=ircmsg)
        if message.command == 'PRIVMSG':
            tags = message.tags
            nick = message.prefix.nick
            where = message.params.middle
            msg = message.params.trailing
            if where[0] == '#':
                _logMessage(where + '#full.log', '< ' + ircmsg, now)
                if nick != 'jtv':
                    _logMessage(where + '#msg.log', nick + ': ' + msg, now)
            if config.botnick in msg.split():
                file = config.botnick + '-Mentions.log'
                _logMessage(file, nick + ' -> ' + where + ': ' + msg, now)
            if where in self._channels:
                chan = self._channels[where]
                ircchannel.commands.parse(chan, tags, nick, msg)
        
        if message.command == 'WHISPER':
            tags = message.tags
            nick = message.prefix.nick
            msg = message.params.trailing
            file = '@' + nick + '@whisper.log'
            _logMessage(file, nick + ': ' + msg, now)
            file = config.botnick + '-All Whisper.log'
            _logMessage(file, nick + ' -> ' + config.botnick + ': ' + msg, now)
            file = config.botnick + '-Raw Whisper.log'
            _logMessage(file, '< ' + ircmsg, now)
            ircwhisper.commands.parse(tags, nick, msg)
        
        if (message.command == 'NOTICE' and message.prefix is not None and
            message.prefix.nick is not None and
            message.params.trailing is not None):
            ircuser.notice.parse(self, message.prefix.nick,
                                 message.params.trailing)
        
        if (message.command == 'NOTICE' and message.prefix is not None and
            message.prefix.nick is None and
            message.params.middle is not None and
            message.params.trailing is not None):
            where = message.params.middle
            if where[0] == '#':
                _logMessage(where + '#full.log', '< ' + ircmsg, now)
        
        if message.command == 'MODE':
            where, mode, nick = message.params.middle.split()
            if where[0] == '#':
                _logMessage(where + '#full.log', '< ' + ircmsg, now)
            if where in self._channels:
                if mode == '+o':
                    self._channels[where].ircOps.add(nick)
                if mode == '-o':
                    self._channels[where].ircOps.discard(nick)
        
        if message.command == 'JOIN':
            where = message.params.middle
            nick = message.prefix.nick
            if where[0] == '#':
                _logMessage(where + '#full.log', '< ' + ircmsg, now)
            if where in self._channels:
                self._channels[where].ircUsers.add(nick)
        
        if message.command == 353:
            where = message.params.middle.split()[-1]
            nicks = message.params.trailing.split(' ')
            if where[0] == '#':
                _logMessage(where + '#full.log', '< ' + ircmsg, now)
            if where in self._channels:
                self._channels[where].ircUsers.update(nicks)
        
        if message.command == 366:
            where = message.params.middle.split()[-1]
            if where[0] == '#':
                _logMessage(where + '#full.log', '< ' + ircmsg, now)
        
        if message.command == 'PART':
            where = message.params.middle
            nick = message.prefix.nick
            if where[0] == '#':
                _logMessage(where + '#full.log', '< ' + ircmsg, now)
            if where in self._channels:
                self._channels[where].ircUsers.discard(nick)

        if message.command == 'PING' and message.params.trailing is not None:
            self.ping(message.params.trailing)
        
        if (message.command == 'PONG' and message.prefix is not None and
            message.prefix.servername is not None and 
            message.prefix.servername == 'tmi.twitch.tv' and
            not message.params.isEmpty and
            message.params.middle == 'tmi.twitch.tv' and
            message.params.trailing == config.botnick):
            self.lastPing = datetime.datetime.now()
        
        if message.command == 'USERSTATE':
            where = message.params.middle
            if where[0] == '#':
                _logMessage(where + '#full.log', '< ' + ircmsg, now)
            if where in self._channels:
                chan = self._channels[where]
                tags = message.tags
                ircuser.userstate.parse(chan, tags)
            pass


class NoPingException(Exception):
    pass


class LoginUnsuccessfulException(Exception):
    pass


def _logMessage(filename, message, timestamp=None):
    if config.ircLogFolder is None:
        return
    logDateFormat = '%Y-%m-%dT%H:%M:%S.%f '
    timestamp = datetime.datetime.utcnow() if timestamp is None else timestamp
    timestampStr = timestamp.strftime(logDateFormat)
    fullfilename = os.path.join(config.ircLogFolder, filename)
    with open(fullfilename, 'a', encoding='utf-8') as file:
        file.write(timestampStr + message + '\n')
