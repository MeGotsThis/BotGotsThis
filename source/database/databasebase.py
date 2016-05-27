from bot.data.return_ import AutoJoinChannel

class DatabaseBase:
    __slots__ = ('_engine', '_connection')
    
    def __init__(self):
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
    
    def getAutoJoinsChats(self):
        return []
        # How to trick Intellisense
        return [AutoJoinChannel('', float('inf'), 'aws')]
    
    def getAutoJoinsPriority(self, broadcaster):
        return float('inf')
    
    def saveAutoJoin(self, broadcaster, priority=0, cluster='aws'):
        return False
    
    def discardAutoJoin(self, broadcaster):
        return False
    
    def setAutoJoinPriority(self, broadcaster, priority):
        return False
    
    def setAutoJoinServer(self, broadcaster, cluster='aws'):
        return False
    
    def getOAuthToken(self, broadcaster):
        return None
    
    def saveBroadcasterToken(self, broadcaster, token):
        pass
    
    def getChatCommands(self, broadcaster, command):
        return {broadcaster: {}, '#global': {}}
    
    def getFullGameTitle(self, abbreviation):
        return None
    
    def insertCustomCommand(self, broadcaster, permission, command,
                            fullMessage, user):
        return False
    
    def updateCustomCommand(self, broadcaster, permission, command,
                            fullMessage, user):
        return False
    
    def replaceCustomCommand(self, broadcaster, permission, command,
                             fullMessage, user):
        return False
    
    def appendCustomCommand(self, broadcaster, permission, command,
                             message, user):
        return False
    
    def deleteCustomCommand(self, broadcaster, permission, command, user):
        return True
    
    def getCustomCommandProperty(self, broadcaster, permission, command,
                                 property=None):
        if property is None:
            return {}
        elif isinstance(property, list):
            return {p: None for p in property}
        else:
            return None
    
    def processCustomCommandProperty(self, broadcaster, permission, command,
                                     property, value):
        return False
    
    def hasFeature(self, broadcaster, feature):
        return False
    
    def addFeature(self, broadcaster, feature):
        return False
    
    def removeFeature(self, broadcaster, feature):
        return True
    
    def listBannedChannels(self):
        return []
    
    def isChannelBannedReason(self, broadcaster):
        return False
    
    def addBannedChannel(self, broadcaster, reason, nick):
        return True
    
    def removeBannedChannel(self, broadcaster, reason, nick):
        return True
    
    def recordTimeout(self, broadcaster, user, fromUser, module, level, length,
                      message, reason):
        return False
    
    def getChatProperty(self, broadcaster, property, default=None, parse=None):
        return default
    
    def getChatProperties(self, broadcaster, properties=[], default=None,
                          parse=None):
        return {}
    
    def setChatProperty(self, broadcaster, property, value=None):
        return False
