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
                                now = dtnow.strftime('< %Y-%m-%d %H:%M:%S.%f ')
                                with open(os.path.join(*pathArgs), 'a',
                                          encoding='utf-8') as file:
                                    file.write(now + ircmsg + '\n')
                            self._parseMsg(ircmsg)
                    except socket.timeout as e:
                        pass
                    sinceLastSend = datetime.datetime.now() - self.lastSentPing
                    sinceLast = datetime.datetime.now() - self.lastPing
                    if sinceLastSend >= datetime.timedelta(minutes=1):
                        self.sendIrcCommand('PING ' + config.botnick + '\n')
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
                        file.write(now.strftime('%Y-%m-%d %H:%M:%S.%f '))
                        file.write('Exception in thread ')
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
    
    def sendIrcCommand(self, command, channel=None):
        if type(command) is str:
            command = command.encode('utf-8')
        try:
            self._ircsock.send(command[:2048])
        except socket.error:
            now = datetime.datetime.now()
            _ = traceback.format_exception(*sys.exc_info())
            if config.exceptionLog is not None:
                with open(config.exceptionLog, 'a',
                            encoding='utf-8') as file:
                    file.write(now.strftime('%Y-%m-%d %H:%M:%S.%f '))
                    file.write('Exception in thread ')
                    file.write(threading.current_thread().name + ':\n')
                    if channel:
                        file.write('Channel: ' + channel + '\n')
                    file.write('Command: ' + command.decode('utf-8') + '\n')
                    file.write(''.join(_))
            self._isConnected = False
        
        if config.ircLogFolder:
            fileName = config.botnick + '-' + self.name + '.log'
            pathArgs = config.ircLogFolder, fileName
            dtnow = datetime.datetime.now()
            now = dtnow.strftime('> %Y-%m-%d %H:%M:%S.%f ')
            with open(os.path.join(*pathArgs), 'a', encoding='utf-8') as file:
                file.write(now + command.decode('utf-8'))
            if channel:
                fileName = channel + '#full.log'
                pathArgs = config.ircLogFolder, fileName
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write(now + command.decode('utf-8'))
                if command.startswith(b'PRIVMSG'):
                    now = dtnow.strftime('[%Y-%m-%d %H:%M:%S.%f] ')
                    fileName = channel + '#msg.log'
                    pathArgs = config.ircLogFolder, fileName
                    with open(os.path.join(*pathArgs), 'a',
                              encoding='utf-8') as file:
                        file.write(now + config.botnick + ': ' +
                                   command.decode('utf-8').split(':', 1)[1])
    
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
        print(str(datetime.datetime.now()) + ' Parted ' + channelData.channel)
    
    def ping(self):
        self.sendIrcCommand('PONG :pingis\n')
        self.lastPing = datetime.datetime.now()

    def _parseMsg(self, ircmsg):
        if ircmsg.find(' PRIVMSG ') != -1:
            parts = ircmsg.split(' ', 3)
            nick = str(parts[0].split('!')[0])[1:]
            where = str(parts[2])
            msg = str(parts[3])[1:]
            if where[0] == '#' and config.ircLogFolder:
                fileName = where + '#full.log'
                pathArgs = config.ircLogFolder, fileName
                dtnow = datetime.datetime.now()
                now = dtnow.strftime('< %Y-%m-%d %H:%M:%S.%f ')
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write(now + ircmsg + '\n')
            if where[0] == '#' and config.ircLogFolder and nick != 'jtv':
                fileName = where + '#msg.log'
                pathArgs = config.ircLogFolder, fileName
                dtnow = datetime.datetime.now()
                now = dtnow.strftime('[%Y-%m-%d %H:%M:%S.%f] ')
                with open(os.path.join(*pathArgs), 'a',
                          encoding='utf-8') as file:
                    file.write(now + nick + ': ' + msg + '\n')
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
        
        if ircmsg.find(' PONG ') != -1:
            self.lastPing = datetime.datetime.now()
            return


class NoPingException(Exception):
    pass


class LoginUnsuccessfulException(Exception):
    pass
