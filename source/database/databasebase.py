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
        return [{'broadcaster': '',
                 'priority': float('inf'),
                 'eventserver': False}]
    
    def getAutoJoinsPriority(self, broadcaster):
        return float('inf')
    
    def saveAutoJoin(self, broadcaster, priority=0, useEvent=False):
        return False
    
    def discardAutoJoin(self, broadcaster):
        return False
    
    def setAutoJoinPriority(self, broadcaster, priority):
        return False
    
    def setAutoJoinServer(self, broadcaster, useEvent=False):
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
    
    def deleteCustomCommand(self, broadcaster, permission, command, user):
        return True
    
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
