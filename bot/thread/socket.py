from .. import config, error, globals, utils
from ..twitchmessage.ircmessage import IrcMessage
from ..twitchmessage.ircparams import IrcMessageParams
from source.ircmessage import parseMessage
import datetime
import socket
import threading
import time

class SocketThread(threading.Thread):
    def __init__(self, server, port, **args):
        threading.Thread.__init__(self, **args)
        self._server = server
        self._port = port
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
            
            globals.join.connected(self)
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
                            utils.logIrcMessage(file, '< ' + ircmsg)
                            parseMessage(self, ircmsg, now)
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
                        raise error.NoPingException()
            except error.NoPingException:
                pass
            except error.LoginUnsuccessfulException:
                pass
            except:
                utils.logException()
            finally:
                self._ircsock.close()
            self._isConnected = False
            globals.join.disconnected(self)
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
            utils.logException(extra)
            self._isConnected = False
        
        now = datetime.datetime.utcnow()
        if message.command == 'PASS':
            message = IrcMessage(command='PASS')
        file = config.botnick + '-' + self.name + '.log'
        utils.logIrcMessage(file, '> ' + str(message), now)
        if whisper:
            file = '@' + whisper[0] + '@whisper.log'
            utils.logIrcMessage(file, config.botnick + ': ' + whisper[1], now)
            file = config.botnick + '-All Whisper.log'
            log = config.botnick + ' -> ' +  whisper[0] + ': ' + whisper[1]
            utils.logIrcMessage(file, log, now)
            file = config.botnick + '-Raw Whisper.log'
            utils.logIrcMessage(file, '> ' + str(message), now)
        elif channel:
            file = channel + '#full.log'
            utils.logIrcMessage(file, '> ' + str(message), now)
            if message.command == 'PRIVMSG':
                file = channel + '#msg.log'
                log = config.botnick + ': ' + message.params.trailing
                utils.logIrcMessage(file, log, now)
    
    def _connect(self):
        self._ircsock.connect((self._server, self._port))
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
        globals.join.part(channelData.channel)
        print(str(datetime.datetime.utcnow()) + ' Parted ' +
              channelData.channel)
    
    def ping(self, message='ping'):
        self.sendIrcCommand(
            IrcMessage(command='PONG',
                       params=IrcMessageParams(trailing=message)))
        self.lastPing = datetime.datetime.now()
