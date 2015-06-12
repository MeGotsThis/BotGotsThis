from config import config
from twitchmessage.ircmessage import IrcMessage
from twitchmessage.ircparams import IrcMessageParams
import ircchannel.commands
import ircuser.notice
import ircuser.userstate
import ircbot.irc
import threading
import traceback
import datetime
import os.path
import socket
import time
import sys

_logDateFormat = '%Y-%m-%d %H:%M:%S.%f'

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
        print(str(datetime.datetime.now()) + ' Starting SocketThread ' +
              self.name)
        
        while self.running:
            self._ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._ircsock.settimeout(5)
            try:
                self._connect()
            except socket.error as e:
                print(str(datetime.datetime.now()) + ' ' + self.name + ' ' +
                      str(e))
                time.sleep(5)
                continue
            self.lastSentPing = datetime.datetime.now()
            self.lastPing = datetime.datetime.now()
            print(str(datetime.datetime.now()) + ' ' + self.name +
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
                            if config.ircLogFolder:
                                fileName = config.botnick + '-' + self.name
                                fileName += '.log'
                                pathArgs = config.ircLogFolder, fileName
                                dtnow = datetime.datetime.now()
                                now = dtnow.strftime(_logDateFormat)
                                with open(os.path.join(*pathArgs), 'a',
                                          encoding='utf-8') as file:
                                    line = '< ' + now + ' ' + ircmsg + '\n'
                                    file.write(line)
                            self._parseMsg(ircmsg)
                    except socket.timeout as e:
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
            except Exception as e:
                now = datetime.datetime.now()
                _ = traceback.format_exception(*sys.exc_info())
                if config.exceptionLog is not None:
                    with open(config.exceptionLog, 'a',
                              encoding='utf-8') as file:
                        file.write(now.strftime(_logDateFormat))
                        file.write(' Exception in thread ')
                        file.write(threading.current_thread().name + ':\n')
                        file.write(''.join(_))
            finally:
                self._ircsock.close()
            self._isConnected = False
            ircbot.irc.join.disconnected(self)
            print(str(datetime.datetime.now()) + ' ' +  self.name +
                  ' Disconnected ' + self._server)
            time.sleep(5)
        print(str(datetime.datetime.now()) + ' Ending SocketThread ' +
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
            now = datetime.datetime.now()
            _ = traceback.format_exception(*sys.exc_info())
            if config.exceptionLog is not None:
                with open(config.exceptionLog, 'a',
                            encoding='utf-8') as file:
                    file.write(now.strftime(_logDateFormat))
                    file.write(' Exception in thread ')
                    file.write(threading.current_thread().name + ':\n')
                    if channel:
                        file.write('Channel: ' + channel + '\n')
                    file.write('Command: ' + str(message) + '\n')
                    file.write(''.join(_))
            self._isConnected = False
        
        if config.ircLogFolder:
            fileName = config.botnick + '-' + self.name + '.log'
            pathArgs = config.ircLogFolder, fileName
            dtnow = datetime.datetime.now()
            now = dtnow.strftime(_logDateFormat)
            with open(os.path.join(*pathArgs), 'a', encoding='utf-8') as file:
                file.write('> ' + now + ' ' + str(message) + '\n')
            if whisper:
                dtnow = datetime.datetime.now()
                now = dtnow.strftime(_logDateFormat)
                fileName = '@' + whisper[0] + '@whisper.log'
                pathArgs = config.ircLogFolder, fileName
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write('[' + now + '] ' + config.botnick + ': ' +
                               whisper[1] + '\n')
                fileName = config.botnick + '-All Whisper.log'
                pathArgs = config.ircLogFolder, fileName
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write('[' + now + '] ' + config.botnick + ' -> ' + 
                                whisper[0] + ': ' + whisper[1] + '\n')
                fileName = config.botnick + '-Raw Whisper.log'
                pathArgs = config.ircLogFolder, fileName
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write('> ' + now + ' ' + str(message) + '\n')
            elif channel:
                fileName = channel + '#full.log'
                pathArgs = config.ircLogFolder, fileName
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write('> ' + now + ' ' + str(message) + '\n')
                if message.command == 'PRIVMSG':
                    now = dtnow.strftime(_logDateFormat)
                    fileName = channel + '#msg.log'
                    pathArgs = config.ircLogFolder, fileName
                    with open(os.path.join(*pathArgs), 'a',
                              encoding='utf-8') as file:
                        line = '[' + now + '] ' + config.botnick + ': '
                        line += message.params.trailing + '\n'
                        file.write(line)
    
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
        print(str(datetime.datetime.now()) + ' Parted ' + channelData.channel)
    
    def ping(self, message='ping'):
        self.sendIrcCommand(
            IrcMessage(command='PONG',
                       params=IrcMessageParams(trailing=message)))
        self.lastPing = datetime.datetime.now()

    def _parseMsg(self, ircmsg):
        message = IrcMessage(message=ircmsg)
        if message.command == 'PRIVMSG':
            tags = message.tags
            nick = message.prefix.nick
            where = message.params.middle
            msg = message.params.trailing
            if where[0] == '#' and config.ircLogFolder:
                fileName = where + '#full.log'
                pathArgs = config.ircLogFolder, fileName
                dtnow = datetime.datetime.now()
                now = dtnow.strftime(_logDateFormat)
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write('< ' + now + ' ' + ircmsg + '\n')
            if where[0] == '#' and config.ircLogFolder and nick != 'jtv':
                fileName = where + '#msg.log'
                pathArgs = config.ircLogFolder, fileName
                dtnow = datetime.datetime.now()
                now = dtnow.strftime(_logDateFormat)
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write('[' + now + '] ' + nick + ': ' + msg + '\n')
            if where in self._channels:
                chan = self._channels[where]
                ircchannel.commands.parse(chan, tags, nick, msg)
        
        if message.command == 'WHISPER':
            tags = message.tags
            nick = message.prefix.nick
            msg = message.params.trailing
            if config.ircLogFolder:
                dtnow = datetime.datetime.now()
                now = dtnow.strftime(_logDateFormat)
                fileName = '@' + nick + '@whisper.log'
                pathArgs = config.ircLogFolder, fileName
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write('[' + now + '] ' + nick + ': ' + msg + '\n')
                fileName = config.botnick + '-All Whisper.log'
                pathArgs = config.ircLogFolder, fileName
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write('[' + now + '] ' + nick + ' -> ' + 
                               config.botnick + ': ' + msg + '\n')
                fileName = config.botnick + '-Raw Whisper.log'
                pathArgs = config.ircLogFolder, fileName
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write('< ' + now + ' ' + ircmsg + '\n')
        
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
            if where[0] == '#' and config.ircLogFolder:
                fileName = where + '#full.log'
                pathArgs = config.ircLogFolder, fileName
                dtnow = datetime.datetime.now()
                now = dtnow.strftime(_logDateFormat)
                with open(os.path.join(*pathArgs), 'a',
                            encoding='utf-8') as file:
                    file.write('< ' + now + ' ' + ircmsg + '\n')
        
        if message.command == 'MODE':
            where = message.params.middle.split()[0]
            if where[0] == '#' and config.ircLogFolder:
                fileName = where + '#full.log'
                pathArgs = config.ircLogFolder, fileName
                dtnow = datetime.datetime.now()
                now = dtnow.strftime(_logDateFormat)
                with open(os.path.join(*pathArgs), 'a',
                            encoding='utf-8') as file:
                    file.write('< ' + now + ' ' + ircmsg + '\n')
        
        if message.command == 'JOIN':
            where = message.params.middle
            nick = message.prefix.nick
            if where[0] == '#' and config.ircLogFolder:
                fileName = where + '#full.log'
                pathArgs = config.ircLogFolder, fileName
                dtnow = datetime.datetime.now()
                now = dtnow.strftime(_logDateFormat)
                with open(os.path.join(*pathArgs), 'a',
                            encoding='utf-8') as file:
                    file.write('< ' + now + ' ' + ircmsg + '\n')
        
        if message.command == 353:
            where = message.params.middle.split()[-1]
            if where[0] == '#' and config.ircLogFolder:
                fileName = where + '#full.log'
                pathArgs = config.ircLogFolder, fileName
                dtnow = datetime.datetime.now()
                now = dtnow.strftime(_logDateFormat)
                with open(os.path.join(*pathArgs), 'a',
                            encoding='utf-8') as file:
                    file.write('< ' + now + ' ' + ircmsg + '\n')
        
        if message.command == 366:
            where = message.params.middle.split()[-1]
            if where[0] == '#' and config.ircLogFolder:
                fileName = where + '#full.log'
                pathArgs = config.ircLogFolder, fileName
                dtnow = datetime.datetime.now()
                now = dtnow.strftime(_logDateFormat)
                with open(os.path.join(*pathArgs), 'a',
                            encoding='utf-8') as file:
                    file.write('< ' + now + ' ' + ircmsg + '\n')
        
        if message.command == 'PART':
            where = message.params.middle
            nick = message.prefix.nick
            if where[0] == '#' and config.ircLogFolder:
                fileName = where + '#full.log'
                pathArgs = config.ircLogFolder, fileName
                dtnow = datetime.datetime.now()
                now = dtnow.strftime(_logDateFormat)
                with open(os.path.join(*pathArgs), 'a',
                            encoding='utf-8') as file:
                    file.write('< ' + now + ' ' + ircmsg + '\n')

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
            if where[0] == '#' and config.ircLogFolder:
                fileName = where + '#full.log'
                pathArgs = config.ircLogFolder, fileName
                dtnow = datetime.datetime.now()
                now = dtnow.strftime(_logDateFormat)
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write('< ' + now + ' ' + ircmsg + '\n')
            if where in self._channels:
                chan = self._channels[where]
                tags = message.tags
                ircuser.userstate.parse(chan, tags)
            pass


class NoPingException(Exception):
    pass


class LoginUnsuccessfulException(Exception):
    pass
