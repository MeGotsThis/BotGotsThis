from config import config
import ircbot.message
import ircbot.socket
import ircbot.join

# Import some necessary libraries.
messaging = ircbot.message.MessageQueue()
mainChat = ircbot.socket.SocketThread(config.mainServer, name='Main Chat')
eventChat = ircbot.socket.SocketThread(config.eventServer, name='Event Chat')
join = ircbot.join.JoinThread()
join.add(mainChat)
join.add(eventChat)
channels = {}

def joinChannel(channel, priority=float('inf'), eventServer=False):
    if channel[0] != '#':
        channel = '#' + channel
    channel = channel.lower()
    if channel in channels:
        channels[channel].joinPriority = min(
            channels[channel].joinPriority, priority)
        return False
    socket = mainChat if not eventServer else eventChat
    channels[channel] = ChannelData(channel, socket, priority)
    socket.joinChannel(channels[channel])
    return True

def partChannel(channel):
    if channel[0] != '#':
        channel = '#' + channel
    if channel in channels:
        channels[channel].part()
        del channels[channel]

ENSURE_REJOIN_TO_MAIN = -2
ENSURE_REJOIN_TO_EVENT = -1
ENSURE_CORRECT = 0
ENSURE_NOT_JOINED = 1

def ensureServer(channel, priority=float('inf'), eventServer=False):
    if channel[0] != '#':
        channel = '#' + channel
    if channel not in channels:
        return ENSURE_NOT_JOINED
    socket = mainChat if not eventServer else eventChat
    if socket is channels[channel].socket:
        channels[channel].joinPriority = min(
            channels[channel].joinPriority, priority)
        return ENSURE_CORRECT
    partChannel(channel)
    joinChannel(channel, priority, eventServer)
    return ENSURE_REJOIN_TO_EVENT if eventServer else ENSURE_REJOIN_TO_MAIN

class ChannelData:
    __slots__ = ['_channel', '_socket', '_twitchStaff', '_twitchAdmin',
                 '_mods', '_subscribers', '_turboUsers', '_users',
                 '_sessionData', '_joinPriority']
    
    def __init__(self, channel, socket, joinPriority=float('inf')):
        self._channel = channel
        self._socket = socket
        self._joinPriority = joinPriority
        self._twitchStaff = set()
        self._twitchAdmin = set()
        self._mods = set()
        self._subscribers = set()
        self._turboUsers = set()
        self._users = set()
        self._sessionData = {}
    
    @property
    def channel(self):
        return self._channel
    
    @property
    def socket(self):
        return self._socket
    
    @property
    def joinPriority(self):
        return self._joinPriority
    
    @joinPriority.setter
    def joinPriority(self, value):
        self._joinPriority = value
    
    @property
    def twitchStaff(self):
        return frozenset(self._twitchStaff)
    
    @property
    def twitchAdmin(self):
        return frozenset(self._twitchAdmin)
    
    @property
    def mods(self):
        return frozenset(self._mods)
    
    @property
    def subscribers(self):
        return frozenset(self._subscribers)
    
    @property
    def turboUsers(self):
        return frozenset(self._turboUsers)
    
    @property
    def users(self):
        return frozenset(self._users)
    
    @property
    def sessionData(self):
        return self._sessionData
    
    def part(self):
        self.socket.partChannel(self)
        messaging.clearQueue(self.channel)
        self._socket = None
    
    def sendMessage(self, msg, priority=1):
        messaging.queueMessage(self, msg, priority)
    
    def sendMulipleMessages(self, messages, priority=1):
        messaging.queueMultipleMessages(self, messages, priority)
    
    def clearTurboUsers(self):
        self._turboUsers.clear()
    
    def addTurboUser(self, user):
        self._turboUsers.add(user)
    
    def clearSubscribers(self):
        self._subscribers.clear()
    
    def addSubscriber(self, subscriber):
        self._subscribers.add(subscriber)
    
    def clearMods(self):
        self._mods.clear()
    
    def addMod(self, mod):
        self._mods.add(mod)
    
    def addTwitchAdmin(self, admin):
        self._twitchAdmin.add(admin)
    
    def addTwitchStaff(self, staff):
        self._twitchStaff.add(staff)
