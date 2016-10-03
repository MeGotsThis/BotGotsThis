import bot.config
# from bot import data  -- https://github.com/python/mypy/issues/1701
from bot.twitchmessage import IrcMessageTagsReadOnly
from typing import Any, Optional


typeTwitchStaff = {'staff'}
typeTwitchAdmin = {'staff', 'admin'}
typeGlobalModerator = {'staff', 'admin', 'global_mod'}
typeModerator = {'staff', 'admin', 'global_mod', 'mod'}


class ChatPermissionSet:
    def __init__(self,
                 tags: Optional[IrcMessageTagsReadOnly],
                 user: str,
                 channel: Any) -> None:
        userType = None  # type: str
        if tags is not None and 'user-type' in tags:
            userType = str(tags['user-type'])
        else:
            userType = ''
        self._tags = tags  # type: Optional[IrcMessageTagsReadOnly]
        self._userType = userType  # type: str
        self._user = user  # type: str
        self._channel = channel
        self._isOwner = None  # type: bool
        self._inOwnerChannel = None  # type: bool
        self._isTwitchStaff = None  # type: bool
        self._isTwitchAdmin = None  # type: bool
        self._isGlobalMod = None  # type: bool
        self._isBroadcaster = None  # type: bool
        self._isModerator = None  # type: bool
        self._isSubscriber = None  # type: bool
        self._isTurbo = None  # type: bool
    
    @property
    def owner(self) -> bool:
        if self._isOwner is None:
            self._isOwner = self._user == bot.config.owner
        return self._isOwner
    
    @property
    def inOwnerChannel(self) -> bool:
        if self._inOwnerChannel is None:
            inOwner = self._channel.channel == bot.config.owner  # type: bool
            inBot = self._channel.channel == bot.config.botnick  # type: bool
            self._inOwnerChannel = inOwner or inBot
        return self._inOwnerChannel
    
    @property
    def twitchStaff(self) -> bool:
        if self._isTwitchStaff is None:
            self._isTwitchStaff = self._userType in typeTwitchStaff
            self._isTwitchStaff = self.owner or self._isTwitchStaff
        return self._isTwitchStaff
    
    @property
    def twitchAdmin(self) -> bool:
        if self._isTwitchAdmin is None:
            self._isTwitchAdmin = self._userType in typeTwitchAdmin
            self._isTwitchAdmin = self.twitchStaff or self._isTwitchAdmin
        return self._isTwitchAdmin
    
    @property
    def globalModerator(self) -> bool:
        if self._isGlobalMod is None:
            self._isGlobalMod = self._userType in typeGlobalModerator
            self._isGlobalMod = self.twitchAdmin or self._isGlobalMod
        return self._isGlobalMod
    
    @property
    def broadcaster(self) -> bool:
        if self._isBroadcaster is None:
            self._isBroadcaster = self._channel.channel == self._user
            self._isBroadcaster = self.globalModerator or self._isBroadcaster
        return self._isBroadcaster
    
    @property
    def moderator(self) -> bool:
        if self._isModerator is None:
            self._isModerator = self._userType in typeModerator
            self._isModerator = self.broadcaster or self._isModerator
        return self._isModerator
    
    @property
    def subscriber(self) -> bool:
        if self._isSubscriber is None:
            subscriber = None  # type: int
            if self._tags is not None and 'subscriber' in self._tags:
                subscriber = int(self._tags['subscriber'])
            else:
                subscriber = 0
            self._isSubscriber = self.broadcaster or bool(subscriber)
        return self._isSubscriber
    
    @property
    def chatModerator(self) -> bool:
        return self._channel.isMod
    
    def __getitem__(self, key: str) -> bool:
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
            if key in ['channelModerator', 'chatModerator']:
                return self.chatModerator
            raise KeyError('unknown permission')
        raise TypeError('key is not of type str')


class WhisperPermissionSet:
    def __init__(self,
                 tags: IrcMessageTagsReadOnly,
                 user: str) -> None:
        userType = None  # type: str
        if 'user-type' in tags:
            userType = str(tags['user-type'])
        else:
            userType = ''
        self._tags = tags  # type: IrcMessageTagsReadOnly
        self._userType = userType  # type: str
        self._user = user  # type: str
        self._isOwner = None  # type: bool
        self._isTwitchStaff = None  # type: bool
        self._isTwitchAdmin = None  # type: bool
        self._isGlobalMod = None  # type: bool
        self._isTurbo = None  # type: bool
    
    @property
    def owner(self) -> bool:
        if self._isOwner is None:
            self._isOwner = self._user == bot.config.owner
        return self._isOwner
    
    @property
    def twitchStaff(self) -> bool:
        if self._isTwitchStaff is None:
            self._isTwitchStaff = self._userType in typeTwitchStaff
            self._isTwitchStaff = self.owner or self._isTwitchStaff
        return self._isTwitchStaff
    
    @property
    def twitchAdmin(self) -> bool:
        if self._isTwitchAdmin is None:
            self._isTwitchAdmin = self._userType in typeTwitchAdmin
            self._isTwitchAdmin = self.twitchStaff or self._isTwitchAdmin
        return self._isTwitchAdmin
    
    @property
    def globalModerator(self) -> bool:
        if self._isGlobalMod is None:
            self._isGlobalMod = self._userType in typeGlobalModerator
            self._isGlobalMod = self.twitchAdmin or self._isGlobalMod
        return self._isGlobalMod
    
    def __getitem__(self, key: str) -> bool:
        if isinstance(key, str):
            if key == 'owner':
                return self.owner
            if key in ['staff', 'twitchStaff']:
                return self.twitchStaff
            if key in ['admin', 'twitchAdmin']:
                return self.twitchAdmin
            if key in ['globalMod', 'globalModerator']:
                return self.globalModerator
            raise KeyError('unknown permission')
        raise TypeError('key is not of type str')
