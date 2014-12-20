import ircbot.irc

class ChannelData:
    __slots__ = ['_channel', '_socket', '_twitchStaff', '_twitchAdmin',
                 '_globalMods', '_mods', '_subscribers', '_turboUsers',
                 '_users', '_sessionData', '_joinPriority']
    
    def __init__(self, channel, socket, joinPriority=float('inf')):
        self._channel = channel
        self._socket = socket
        self._joinPriority = joinPriority
        self._twitchStaff = set()
        self._twitchAdmin = set()
        self._globalMods = set()
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
    def globalMods(self):
        return frozenset(self._globalMods)
    
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
        ircbot.irc.messaging.queueMessage(self, msg, priority)
    
    def sendMulipleMessages(self, messages, priority=1):
        ircbot.irc.messaging.queueMultipleMessages(self, messages, priority)
    
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
    
    def addGlobalMod(self, mod):
        self._globalMods.add(mod)
    
    def addTwitchAdmin(self, admin):
        self._twitchAdmin.add(admin)
    
    def addTwitchStaff(self, staff):
        self._twitchStaff.add(staff)
