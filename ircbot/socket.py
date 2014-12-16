from config import config
import ircchannel.commands
import ircuser.notice
import ircbot.irc
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
        print('Starting SocketThread ' + self.name)
        
        while self.running:
            self._ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._ircsock.settimeout(5)
            try:
                self._connect()
            except socket.error as e:
                print(e)
                time.sleep(5)
                continue
            self.lastPing = datetime.datetime.now()
            print(self.name + ' Connected ' + self._server)
            
            ircbot.irc.join.connected(self)
            self._isConnected = True
            try:
                while self.running:
                    try:
                        ircmsgs = lastRecv = self._ircsock.recv(2048)
                        while lastRecv[-2:] != b'\r\n':
                            lastRecv = self._ircsock.recv(2048)
                            ircmsgs += lastRecv
                        
                        for ircmsg in ircmsgs.split(b'\r\n'):
                            if not ircmsg:
                                continue
                            ircmsg = ircmsg.decode('utf-8')
                            if config.ircLogFolder:
                                fileName = config.botnick + '-' + self.name
                                fileName += '.log'
                                pathArgs = config.ircLogFolder, fileName
                                dtnow = datetime.datetime.now()
                                now = dtnow.strftime('< %Y-%m-%d %H:%M:%S.%f ')
                                with open(os.path.join(*pathArgs), 'a',
                                          encoding='utf-8') as file:
                                    file.write(now + ircmsg + '\n')
                            self._parseMsg(ircmsg)
                    except socket.timeout as e:
                        pass
                    sinceLast = datetime.datetime.now() - self.lastPing
                    if sinceLast >= datetime.timedelta(minutes=6):
                        raise NoPingException()
            except NoPingException:
                pass
            except LoginUnsuccessfulException:
                pass
            except Exception as e:
                now = datetime.datetime.now()
                exc_type, exc_value, exc_traceback = sys.exc_info()
                _ = traceback.format_exception(
                    exc_type, exc_value, exc_traceback)
                if config.exceptionLog is not None:
                    with open(config.exceptionLog, 'a',
                              encoding='utf-8') as file:
                        file.write(now.strftime('%Y-%m-%d %H:%M:%S.%f '))
                        file.write(' ' + ''.join(_))
            finally:
                self._ircsock.close()
            self._isConnected = False
            ircbot.irc.join.disconnected(self)
            print(self.name + ' Disconnected ' + self._server)
            time.sleep(5)
        print('Ending SocketThread ' + self.name)
    
    def sendIrcCommand(self, command, channel=None):
        if type(command) is str:
            command = command.encode('utf-8')
        self._ircsock.send(command[:2048])
        if config.ircLogFolder:
            fileName = config.botnick + '-' + self.name + '.log'
            pathArgs = config.ircLogFolder, fileName
            dtnow = datetime.datetime.now()
            now = dtnow.strftime('> %Y-%m-%d %H:%M:%S.%f ')
            with open(os.path.join(*pathArgs), 'a', encoding='utf-8') as file:
                file.write(now + command.decode('utf-8'))
            if channel:
                fileName = channel + '.log'
                pathArgs = config.ircLogFolder, fileName
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write(now + command.decode('utf-8'))
    
    def _connect(self):
        self._ircsock.connect((self._server, 6667))
        comms = ['PASS ' + config.password + '\n',
                 'NICK ' + config.botnick + '\n',
                 'USER ' + config.botnick + ' 0 * :' + config.botnick + '\n',
                 'TWITCHCLIENT 3\n',
                 ]
        for comm in comms:
            self.sendIrcCommand(comm)
    
    def joinChannel(self, channelData):
        with self._channelsLock:
            self._channels[channelData.channel] = channelData
    
    def partChannel(self, channelData):
        with self._channelsLock:
            self.sendIrcCommand('PART ' + channelData.channel + '\n',
                                channelData.channel)
            del self._channels[channelData.channel]
        ircbot.irc.join.part(channelData.channel)
        print('Parted ' + channelData.channel)
    
    def ping(self):
        self.sendIrcCommand('PONG :pingis\n')
        self.lastPing = datetime.datetime.now()

    def _parseMsg(self, ircmsg):
        if where[0] == '#' and config.ircLogFolder:
            fileName = where + '.log'
            pathArgs = config.ircLogFolder, fileName
            dtnow = datetime.datetime.now()
            now = dtnow.strftime('< %Y-%m-%d %H:%M:%S.%f ')
            with open(os.path.join(*pathArgs), 'a',
                      encoding='utf-8') as file:
                file.write(now + ircmsg + '\n')
        
        if ircmsg.find(' PRIVMSG ') != -1:
            parts = ircmsg.split(' ', 3)
            nick = parts[0].split('!')[0][1:]
            where = parts[2]
            msg = parts[3][1:]
            if where in self._channels:
                ircchannel.commands.parse(self._channels[where], nick, msg)
            return
        
        if ircmsg.find(' NOTICE ') != -1:
            parts = ircmsg.split(' ', 3)
            nick = parts[0].split('!')[0][1:]
            msg = parts[3][1:]
            if msg == 'Login unsuccessful':
                ircuser.notice.parse(self, nick, msg)
            return
        
        if ircmsg.find('PING :') != -1:
            self.ping()
            return


class NoPingException(Exception):
    pass


class LoginUnsuccessfulException(Exception):
    pass
