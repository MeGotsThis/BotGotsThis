from config import config
import ircchannel.commands
import ircuser.notice
import ircuser.user
import ircbot.message
import threading
import traceback
import datetime
import os.path
import socket
import time
import sys

# Import some necessary libraries.
messaging = ircbot.message.MessgeQueue()
channels = {}

def joinChannel(channel):
    if channel[0] != '#':
        channel = '#' + channel
    channel = channel.lower()
    if channel in channels:
        return False
    channels[channel] = ChannelSocketThread(name=channel, channel=channel)
    channels[channel].start()
    return True

def partChannel(channel):
    if channel[0] != '#':
        channel = '#' + channel
    if channel in channels:
        channels[channel].part()
        del channels[channel]

class ChannelSocketThread(threading.Thread):
    def __init__(self, channel, **args):
        threading.Thread.__init__(self, **args)
        self.channel = channel
        self.twitchStaff = []
        self.twitchAdmin = []
        self.mods = []
        self.users = []
        self.running = True
    
    def run(self):
        print('Starting ' + self.channel)
        
        while self.running:
            self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ircsock.settimeout(5)
            try:
                self._connect()
            except socket.error as e:
                print(e)
                time.sleep(5)
                continue
            self.lastPing = datetime.datetime.now()
            print('Connected ' + self.channel)
            
            try:
                while self.running:
                    try:
                        ircmsgs = lastRecv = self.ircsock.recv(2048)
                        while lastRecv[-2:] != b'\r\n':
                            lastRecv = self.ircsock.recv(2048)
                            ircmsgs += lastRecv
                        
                        for ircmsg in ircmsgs.split(b'\r\n'):
                            if not ircmsg:
                                continue
                            ircmsg = ircmsg.decode('utf-8')
                            if config.ircLogFolder:
                                fileName = self.channel + '.log'
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
            except Exception as e:
                now = datetime.datetime.now()
                messaging.clearQueue(self.channel)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                _ = traceback.format_exception(
                    exc_type, exc_value, exc_traceback)
                if config.exceptionLog is not None:
                    with open(config.exceptionLog, 'a',
                              encoding='utf-8') as file:
                        file.write(now.strftime('%Y-%m-%d %H:%M:%S.%f '))
                        file.write(' ' + ''.join(_))
                if config.ircLogFolder:
                    fileName = self.channel + '.log'
                    pathArgs = config.ircLogFolder, fileName
                    with open(os.path.join(*pathArgs), 'a',
                              encoding='utf-8') as file:
                        file.write(' ' + ''.join(_))
            finally:
                self.ircsock.close()
            print('Disconnected ' + self.channel)
            time.sleep(5)
        print('Ending ' + self.channel)
    
    def sendIrcCommand(self, command):
        # Makes an IRC command over to the server
        
        if type(command) is str:
            command = command.encode('utf-8')
        self.ircsock.send(command[:2048])
        if config.ircLogFolder:
            fileName = self.channel + '.log'
            pathArgs = config.ircLogFolder, fileName
            dtnow = datetime.datetime.now()
            now = dtnow.strftime('> %Y-%m-%d %H:%M:%S.%f ')
            with open(os.path.join(*pathArgs), 'a', encoding='utf-8') as file:
                file.write(now + command.decode('utf-8'))
    
    def _connect(self):
        # Connect to IRC server
        
        self.ircsock.connect((config.server, 6667))
        comms = ['PASS ' + config.password + '\n',
                 'NICK ' + config.botnick + '\n',
                 'USER ' + config.botnick + ' 0 * :' + config.botnick + '\n',
                 'JOIN ' + self.channel + '\n',
                 ]
        for comm in comms:
            self.sendIrcCommand(comm)
        
        self.sendMessage('.mods')
    
    def part(self):
        self.sendIrcCommand('PART ' + self.channel + '\n')
        messaging.clearQueue(self.channel)
        self.running = False
    
    def ping(self):
        self.sendIrcCommand('PONG :pingis\n')
        self.lastPing = datetime.datetime.now()

    def sendMessage(self, msg, priority=1):
        messaging.queueMessage(self, msg, priority)
    
    def sendMulipleMessages(self, messages, priority=1):
        messaging.queueMultipleMessages(self, messages, priority)
    
    def _parseMsg(self, ircmsg):
        if ircmsg.find(' PRIVMSG ') != -1:
            parts = ircmsg.split(' ', 3)
            nick = parts[0].split('!')[0][1:]
            where = parts[2]
            msg = parts[3][1:]
            if where == self.channel:
                ircchannel.commands.parse(self, nick, msg)
            if where == config.botnick:
                ircuser.user.parse(self, nick, msg)
            return
        
        if ircmsg.find(' NOTICE ') != -1:
            parts = ircmsg.split(' ', 3)
            nick = parts[0].split('!')[0][1:]
            msg = parts[3][1:]
            if msg == 'Login unsuccessful':
                ircuser.notice.parse(self, nick, msg)
            return
        
        if ircmsg.find(' 353 ') != -1:
            parts = ircmsg.split(' ', 5)
            channel = parts[4]
            nicks = parts[5][1:].split(' ')
            if channel == self.channel:
                for nick in nicks:
                    self.users.append(nick)
            return
        
        if ircmsg.find(' JOIN ') != -1:
            parts = ircmsg.split(' ', 2)
            nick = parts[0].split('!')[0][1:]
            channel = parts[2]
            if channel == self.channel:
                self.users.append(nick)
            return
        
        if ircmsg.find(' PART ') != -1:
            parts = ircmsg.split(' ', 2)
            nick = parts[0].split('!')[0][1:]
            channel = parts[2]
            if channel == self.channel and nick in self.users:
                self.users.remove(nick)
            return
        
        if ircmsg.find('PING :') != -1:
            self.ping()
            return

class NoPingException(Exception):
    pass

class LoginUnsuccessfulException(Exception):
    pass
