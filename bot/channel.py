from source.api.ffz import getBroadcasterEmotes
from . import globals
import datetime

class Channel:
    __slots__ = ['_channel', '_ircChannel', '_socket', '_isMod',
                 '_isSubscriber', '_ircUsers', '_ircOps', '_sessionData',
                 '_joinPriority', '_ffzEmotes', '_ffzCache', '_streamingSince',
                 '_twitchStatus', '_twitchGame',
                 ]
    
    def __init__(self, channel, socket, joinPriority=float('inf')):
        self._channel = channel
        self._ircChannel = '#' + channel
        self._socket = socket
        self._isMod = False
        self._isSubscriber = False
        self._ircUsers = set()
        self._ircOps = set()
        self._joinPriority = float(joinPriority)
        self._sessionData = {}
        self._ffzEmotes = {}
        self._ffzCache = datetime.datetime.min
        self._streamingSince = None
        self._twitchStatus = None
        self._twitchGame = None
    
    @property
    def channel(self):
        return self._channel
    
    @property
    def ircChannel(self):
        return self._ircChannel
    
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
    def ffzCache(self):
        return self._ffzCache
    
    @property
    def ffzEmotes(self):
        return self._ffzEmotes
    
    @property
    def streamingSince(self):
        return self._streamingSince
    
    @streamingSince.setter
    def streamingSince(self, value):
        self._streamingSince = value
    
    @property
    def isStreaming(self):
        return self._streamingSince is not None
    
    @property
    def twitchStatus(self):
        return self._twitchStatus
    
    @twitchStatus.setter
    def twitchStatus(self, value):
        self._twitchStatus = value
    
    @property
    def twitchGame(self):
        return self._twitchGame
    
    @twitchGame.setter
    def twitchGame(self, value):
        self._twitchGame = value
    
    def onJoin(self):
        self._ircUsers.clear()
        self._ircOps.clear()
    
    def part(self):
        self.socket.partChannel(self)
        globals.messaging.clearQueue(self.channel)
        self._socket = None
    
    def sendMessage(self, msg, priority=1):
        globals.messaging.queueMessage(self, msg, priority)
    
    def sendMulipleMessages(self, messages, priority=1):
        globals.messaging.queueMultipleMessages(self, messages, priority)
    
    def updateFfzEmotes(self):
        self._ffzCache = datetime.datetime.utcnow()
        emotes = getBroadcasterEmotes(self._channel[1:])
        self._ffzEmotes = emotes or self._ffzEmotes
