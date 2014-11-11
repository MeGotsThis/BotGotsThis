from config import config
import ircchannel.commands
import ircuser.user
import ircbot.message
import threading
import traceback
import datetime
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
        self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ircsock.settimeout(5)
        self._connect()

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
                        msg = ircmsg.decode(sys.stdout.encoding, 'replace')
                        now = datetime.datetime.now().strftime(' %H:%M:%S.%f ')
                        print(self.channel + now + msg)
                        ircmsg = ircmsg.decode('utf-8')
                        self._parseMsg(ircmsg)
                except socket.error as e:
                    pass
        except Exception as e:
            now = datetime.datetime.now()
            messaging.clearQueue(self.channel)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            _ = traceback.format_exception(exc_type, exc_value, exc_traceback)
            if config.exceptionLog is not None:
                with open(config.exceptionLog, 'a') as file:
                    file.write(now.strftime('%Y-%m-%d %H:%M:%S.%f '))
                    file.write(' ' + ''.join(_))
            raise
        finally:
            partChannel(self.channel)
    
    def sendIrcCommand(self, command):
        # Makes an IRC command over to the server
        
        if type(command) is str:
            command = command.encode('utf-8')
        self.ircsock.send(command[:2048])
    
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

    def sendMessage(self, msg, priority=1):
        messaging.queueMessage(self, msg, priority)
    
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
