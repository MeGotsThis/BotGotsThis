import ircbot.irc

class ChannelData:
    __slots__ = ['_channel', '_socket', '_isMod',
                 '_isSubscriber', '_sessionData', '_joinPriority']
    
    def __init__(self, channel, socket, joinPriority=float('inf')):
        self._channel = channel
        self._socket = socket
        self._isMod = False
        self._isSubscriber = False
        self._joinPriority = float(joinPriority)
        self._sessionData = {}
    
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
    def joinPriority(self):
        return self._joinPriority
    
    @joinPriority.setter
    def joinPriority(self, value):
        self._joinPriority = float(value)
    
    @property
    def sessionData(self):
        return self._sessionData
    
    def part(self):
        self.socket.partChannel(self)
        ircbot.irc.messaging.clearQueue(self.channel)
        self._socket = None
    
    def sendMessage(self, msg, priority=1):
        ircbot.irc.messaging.queueMessage(self, msg, priority)
    
    def sendMulipleMessages(self, messages, priority=1):
        ircbot.irc.messaging.queueMultipleMessages(self, messages, priority)
