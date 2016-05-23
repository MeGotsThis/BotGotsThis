from bot import config

typeTwitchStaff = ['staff']
typeTwitchAdmin = ['staff', 'admin']
typeGlobalModerator = ['staff', 'admin', 'global_mod']
typeModerator = ['staff', 'admin', 'global_mod', 'mod']

class ChatPermissionSet:
    def __init__(self, tags, user, channel):
        if 'user-type' in tags:
            userType = tags['user-type']
        else:
            userType = ''
        self._tags = tags
        self._userType = userType
        self._user = user
        self._channel = channel
        self._isOwner = None
        self._inOwnerChannel = None
        self._isTwitchStaff = None
        self._isTwitchAdmin = None
        self._isGlobalMod = None
        self._isBroadcaster = None
        self._isModerator = None
        self._isSubscriber = None
        self._isTurbo = None
    
    @property
    def owner(self):
        if self._isOwner is None:
            self._isOwner = self._user == config.owner
        return self._isOwner
    
    @property
    def inOwnerChannel(self):
        if self._inOwnerChannel is None:
            inOwner = self._channel.channel == config.owner
            inBot = self._channel.channel == config.botnick
            self._inOwnerChannel = inOwner or inBot
        return self._inOwnerChannel
    
    @property
    def twitchStaff(self):
        if self._isTwitchStaff is None:
            self._isTwitchStaff = self._userType == typeTwitchStaff
            self._isGlobalMod = self.owner or self._isGlobalMod
        return self._isTwitchStaff
    
    @property
    def twitchAdmin(self):
        if self._isTwitchAdmin is None:
            self._isTwitchAdmin = self._userType == typeTwitchAdmin
            self._isGlobalMod = self.twitchStaff or self._isGlobalMod
        return self._isTwitchAdmin
    
    @property
    def globalModerator(self):
        if self._isGlobalMod is None:
            self._isGlobalMod = self._userType == typeGlobalModerator
            self._isGlobalMod = self.twitchAdmin or self._isGlobalMod
        return self._isGlobalMod
    
    @property
    def broadcaster(self):
        if self._isBroadcaster is None:
            self._isBroadcaster = self._channel.channel == self._user
            self._isBroadcaster = self.globalModerator or self._isBroadcaster
        return self._isBroadcaster
    
    @property
    def moderator(self):
        if self._isModerator is None:
            self._isModerator = self._userType == typeModerator
            self._isModerator = self.broadcaster or self._isModerator
        return self._isModerator
    
    @property
    def subscriber(self):
        if self._isSubscriber is None:
            if 'subscriber' in self._tags:
                subscriber = self._tags['subscriber']
            else:
                subscriber = 0
            self._isSubscriber = self.broadcaster or bool(int(subscriber))
        return self._isSubscriber
    
    @property
    def turbo(self):
        if self._isTurbo is None:
            if 'turbo' in self._tags:
                turbo = self._tags['turbo']
            else:
                turbo = 0
            self._isTurbo = self.broadcaster or bool(int(turbo))
        return self._isTurbo
    
    @property
    def chatModerator(self):
        return self._channel.isMod
    
    def __getitem__(self, key):
        if isinstance(key, str):
            if key == 'owner':
                return self.owner
            if key in ['ownerChan', 'inOwnerChannel']:
                return self.inOwnerChannel
            if key in ['staff', 'twitchStaff']:
                return self.twitchStaff
            if key in ['admin', 'twitchAdmin']:
                return self.twitchAdmin
            if key in ['globalMod', 'globalModerator']:
                return self.globalModerator
            if key == 'broadcaster':
                return self.broadcaster
            if key == 'moderator':
                return self.moderator
            if key == 'subscriber':
                return self.subscriber
            if key == 'turbo':
                return self.turbo
            if key in ['channelModerator', 'chatModerator']:
                return self.chatModerator
            raise KeyError('unknown permission')
        raise TypeError('key is not of type str')

class WhisperPermissionSet:
    def __init__(self, tags, user):
        if 'user-type' in tags:
            userType = tags['user-type']
        else:
            userType = ''
        self._tags = tags
        self._userType = userType
        self._user = user
        self._isOwner = None
        self._isTwitchStaff = None
        self._isTwitchAdmin = None
        self._isGlobalMod = None
        self._isTurbo = None
    
    @property
    def owner(self):
        if self._isOwner is None:
            self._isOwner = self._user == config.owner
        return self._isOwner
    
    @property
    def twitchStaff(self):
        if self._isTwitchStaff is None:
            self._isTwitchStaff = self._userType == typeTwitchStaff
            self._isGlobalMod = self.owner or self._isGlobalMod
        return self._isTwitchStaff
    
    @property
    def twitchAdmin(self):
        if self._isTwitchAdmin is None:
            self._isTwitchAdmin = self._userType == typeTwitchAdmin
            self._isGlobalMod = self.twitchStaff or self._isGlobalMod
        return self._isTwitchAdmin
    
    @property
    def globalModerator(self):
        if self._isGlobalMod is None:
            self._isGlobalMod = self._userType == typeGlobalModerator
            self._isGlobalMod = self.twitchAdmin or self._isGlobalMod
        return self._isGlobalMod
    
    @property
    def turbo(self):
        if self._isTurbo is None:
            if 'turbo' in self._tags:
                turbo = self._tags['turbo']
            else:
                turbo = 0
            self._isTurbo = self.broadcaster or bool(int(turbo))
        return self._isTurbo
    
    def __getitem__(self, key):
        if isinstance(key, str):
            if key == 'owner':
                return self.owner
            if key in ['staff', 'twitchStaff']:
                return self.twitchStaff
            if key in ['admin', 'twitchAdmin']:
                return self.twitchAdmin
            if key in ['globalMod', 'globalModerator']:
                return self.globalModerator
            if key == 'turbo':
                return self.turbo
            raise KeyError('unknown permission')
        raise TypeError('key is not of type str')
