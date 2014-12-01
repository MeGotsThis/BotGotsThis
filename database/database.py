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
    
    def getOAuthToken(self, broadcaster):
        return None
    
    def saveBroadcasterToken(self, broadcaster, token):
        pass
    
    def getChatCommands(self, broadcaster, command):
        return {broadcaster: {}, '#global': {}}
    
    def getFullGameTitle(self, abbreviation):
        return None

