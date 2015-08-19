import datetime
import ircbot.ffzApi
import ircbot.irc

class ChannelData:
    __slots__ = ['_channel', '_socket', '_isMod', '_isSubscriber', '_ircUsers',
                 '_ircOps', '_sessionData', '_joinPriority', '_ffzEmotes',
                 '_ffzCache',
                 ]
    
    def __init__(self, channel, socket, joinPriority=float('inf')):
        self._channel = channel
        self._socket = socket
        self._isMod = False
        self._isSubscriber = False
        self._ircUsers = set()
        self._ircOps = set()
        self._joinPriority = float(joinPriority)
        self._sessionData = {}
        self._ffzEmotes = {}
        self._ffzCache = datetime.datetime.min
    
    @property
    def channel(self):
        return self._channel
    
    @property
    def socket(self):
        return self._socket
    
    @property
    def isMod(self):
        return self._isMod
    
    @isMod.setter
    def isMod(self, value):
        self._isMod = bool(value)
    
    @property
    def isSubscriber(self):
        return self._isSubscriber
    
    @isSubscriber.setter
    def isSubscriber(self, value):
        self._isSubscriber = bool(value)
    
    @property
    def ircUsers(self):
        return self._ircUsers
    
    @property
    def ircOps(self):
        return self._ircOps
    
    @property
    def joinPriority(self):
        return self._joinPriority
    
    @joinPriority.setter
    def joinPriority(self, value):
        self._joinPriority = float(value)
    
    @property
    def sessionData(self):
        return self._sessionData
    
    @property
    def ffzEmotes(self):
        currentTime = datetime.datetime.utcnow()
        if currentTime - self._ffzCache >= datetime.timedelta(hours=1):
            emotes = ircbot.ffzApi.getBroadcasterEmotes(self._channel[1:])
            self._ffzEmotes = emotes or self._ffzEmotes
        return self._ffzEmotes
    
    def onJoin(self):
        self._ircUsers.clear()
        self._ircOps.clear()
    
    def part(self):
        self.socket.partChannel(self)
        ircbot.irc.messaging.clearQueue(self.channel)
        self._socket = None
    
    def sendMessage(self, msg, priority=1):
        ircbot.irc.messaging.queueMessage(self, msg, priority)
    
    def sendMulipleMessages(self, messages, priority=1):
        ircbot.irc.messaging.queueMultipleMessages(self, messages, priority)
