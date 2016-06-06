from abc import ABCMeta, abstractmethod

class DatabaseBase(metaclass=ABCMeta):
    __slots__ = ('_engine', '_connection')
    
    def __init__(self, **kwargs):
        self._engine = 'None'
        self._connection = None
    
    @property
    def engine(self):
        return self._engine
    
    @property
    def connection(self):
        return self._connection
    
    def __enter__(self):
        self._connection = None
        return self
    
    def __exit__(self, type, value, traceback):
        if self.connection is not None:
            self.connection.close()
    
    @abstractmethod
    def getAutoJoinsChats(self):
        yield from []
    
    @abstractmethod
    def getAutoJoinsPriority(self, broadcaster):
        return float('inf')
    
    @abstractmethod
    def saveAutoJoin(self, broadcaster, priority=0, cluster='aws'):
        return False
    
    @abstractmethod
    def discardAutoJoin(self, broadcaster):
        return False
    
    @abstractmethod
    def setAutoJoinPriority(self, broadcaster, priority):
        return False
    
    @abstractmethod
    def setAutoJoinServer(self, broadcaster, cluster='aws'):
        return False
    
    @abstractmethod
    def getOAuthToken(self, broadcaster):
        return None
    
    @abstractmethod
    def saveBroadcasterToken(self, broadcaster, token):
        pass
    
    @abstractmethod
    def getChatCommands(self, broadcaster, command):
        return {broadcaster: {}, '#global': {}}
    
    @abstractmethod
    def getFullGameTitle(self, abbreviation):
        return None
    
    @abstractmethod
    def insertCustomCommand(self, broadcaster, permission, command,
                            fullMessage, user):
        return False
    
    @abstractmethod
    def updateCustomCommand(self, broadcaster, permission, command,
                            fullMessage, user):
        return False
    
    @abstractmethod
    def replaceCustomCommand(self, broadcaster, permission, command,
                             fullMessage, user):
        return False
    
    @abstractmethod
    def appendCustomCommand(self, broadcaster, permission, command,
                             message, user):
        return False
    
    @abstractmethod
    def deleteCustomCommand(self, broadcaster, permission, command, user):
        return True
    
    @abstractmethod
    def getCustomCommandProperty(self, broadcaster, permission, command,
                                 property=None):
        if property is None:
            return {}
        elif isinstance(property, list):
            return {p: None for p in property}
        else:
            return None
    
    @abstractmethod
    def processCustomCommandProperty(self, broadcaster, permission, command,
                                     property, value):
        return False
    
    @abstractmethod
    def hasFeature(self, broadcaster, feature):
        return False
    
    @abstractmethod
    def addFeature(self, broadcaster, feature):
        return False
    
    @abstractmethod
    def removeFeature(self, broadcaster, feature):
        return True
    
    @abstractmethod
    def listBannedChannels(self):
        yield from []
    
    @abstractmethod
    def isChannelBannedReason(self, broadcaster):
        return None
    
    @abstractmethod
    def addBannedChannel(self, broadcaster, reason, nick):
        return True
    
    @abstractmethod
    def removeBannedChannel(self, broadcaster, reason, nick):
        return True
    
    @abstractmethod
    def recordTimeout(self, broadcaster, user, fromUser, module, level, length,
                      message, reason):
        return False
    
    @abstractmethod
    def getChatProperty(self, broadcaster, property, default=None, parse=None):
        return default
    
    @abstractmethod
    def getChatProperties(self, broadcaster, properties=(), default=None,
                          parse=None):
        return {}
    
    @abstractmethod
    def setChatProperty(self, broadcaster, property, value=None):
        return False
