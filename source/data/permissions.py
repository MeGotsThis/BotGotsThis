import bot
# from bot import data  -- https://github.com/python/mypy/issues/1701
from bot.twitchmessage import IrcMessageTagsReadOnly
from typing import Any, Optional, Set


typeTwitchStaff: Set[str] = {'staff'}
typeTwitchAdmin: Set[str] = {'staff', 'admin'}
typeGlobalModerator: Set[str] = {'staff', 'admin', 'global_mod'}
typeModerator: Set[str] = {'staff', 'admin', 'global_mod', 'mod'}


class ChatPermissionSet:
    def __init__(self,
                 tags: Optional[IrcMessageTagsReadOnly],
                 user: str,
                 channel: Any,
                 permitted: bool,
                 manager: bool) -> None:
        userType: str
        if tags is not None and 'user-type' in tags:
            userType = str(tags['user-type'])
        else:
            userType = ''
        self._tags: Optional[IrcMessageTagsReadOnly] = tags
        self._userType: str = userType
        self._user: str = user
        self._channel: Any = channel
        self._isOwner: bool
        self._isManager: bool = manager
        self._inOwnerChannel: bool
        self._isTwitchStaff: bool
        self._isTwitchAdmin: bool
        self._isGlobalMod: bool
        self._isBroadcaster: bool
        self._isModerator: bool
        self._isSubscriber: bool
        self._permitted: bool = permitted
        self._bannable: bool

    @property
    def owner(self) -> bool:
        if not hasattr(self, '_isOwner'):
            self._isOwner = self._user == bot.config.owner
        return self._isOwner
    
    @property
    def inOwnerChannel(self) -> bool:
        if not hasattr(self, '_inOwnerChannel'):
            inOwner: bool = self._channel.channel == bot.config.owner
            inBot: bool = self._channel.channel == bot.config.botnick
            self._inOwnerChannel = inOwner or inBot
        return self._inOwnerChannel

    @property
    def manager(self) -> bool:
        return self._isManager or self.owner

    @property
    def twitchStaff(self) -> bool:
        if not hasattr(self, '_isTwitchStaff'):
            self._isTwitchStaff = self._userType in typeTwitchStaff
            self._isTwitchStaff = self.manager or self._isTwitchStaff
        return self._isTwitchStaff
    
    @property
    def twitchAdmin(self) -> bool:
        if not hasattr(self, '_isTwitchAdmin'):
            self._isTwitchAdmin = self._userType in typeTwitchAdmin
            self._isTwitchAdmin = self.twitchStaff or self._isTwitchAdmin
        return self._isTwitchAdmin
    
    @property
    def globalModerator(self) -> bool:
        if not hasattr(self, '_isGlobalMod'):
            self._isGlobalMod = self._userType in typeGlobalModerator
            self._isGlobalMod = self.twitchAdmin or self._isGlobalMod
        return self._isGlobalMod
    
    @property
    def broadcaster(self) -> bool:
        if not hasattr(self, '_isBroadcaster'):
            self._isBroadcaster = self._channel.channel == self._user
            self._isBroadcaster = self.globalModerator or self._isBroadcaster
        return self._isBroadcaster
    
    @property
    def moderator(self) -> bool:
        if not hasattr(self, '_isModerator'):
            self._isModerator = self._userType in typeModerator
            self._isModerator = self.broadcaster or self._isModerator
        return self._isModerator

    @property
    def subscriber(self) -> bool:
        if not hasattr(self, '_isSubscriber'):
            subscriber: int
            if self._tags is not None and 'subscriber' in self._tags:
                subscriber = int(self._tags['subscriber'])
            else:
                subscriber = 0
            self._isSubscriber = self.broadcaster or bool(subscriber)
        return self._isSubscriber

    @property
    def permitted(self) -> bool:
        return not self.bannable or self._permitted

    @property
    def bannable(self) -> bool:
        if not hasattr(self, '_bannable'):
            self._bannable = (self._userType not in typeModerator
                              and self._channel.channel != self._user)
        return self._bannable
    
    @property
    def chatModerator(self) -> bool:
        return self._channel.isMod
    
    def __getitem__(self, key: str) -> bool:
        if isinstance(key, str):
            if key == 'owner':
                return self.owner
            if key == 'manager':
                return self.manager
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
            if key == 'permitted':
                return self.permitted
            if key == 'bannable':
                return self.bannable
            if key in ['channelModerator', 'chatModerator']:
                return self.chatModerator
            raise KeyError('unknown permission')
        raise TypeError('key is not of type str')


class WhisperPermissionSet:
    def __init__(self,
                 tags: IrcMessageTagsReadOnly,
                 user: str,
                 manager: bool) -> None:
        userType: str
        if 'user-type' in tags:
            userType = str(tags['user-type'])
        else:
            userType = ''
        self._tags: IrcMessageTagsReadOnly = tags
        self._userType: str = userType
        self._user: str = user
        self._isOwner: bool
        self._isManager: bool = manager
        self._isTwitchStaff: bool
        self._isTwitchAdmin: bool
        self._isGlobalMod: bool
        self._isTurbo: bool
    
    @property
    def owner(self) -> bool:
        if not hasattr(self, '_isOwner'):
            self._isOwner = self._user == bot.config.owner
        return self._isOwner

    @property
    def manager(self) -> bool:
        return self._isManager or self.owner

    @property
    def twitchStaff(self) -> bool:
        if not hasattr(self, '_isTwitchStaff'):
            self._isTwitchStaff = self._userType in typeTwitchStaff
            self._isTwitchStaff = self.manager or self._isTwitchStaff
        return self._isTwitchStaff
    
    @property
    def twitchAdmin(self) -> bool:
        if not hasattr(self, '_isTwitchAdmin'):
            self._isTwitchAdmin = self._userType in typeTwitchAdmin
            self._isTwitchAdmin = self.twitchStaff or self._isTwitchAdmin
        return self._isTwitchAdmin
    
    @property
    def globalModerator(self) -> bool:
        if not hasattr(self, '_isGlobalMod'):
            self._isGlobalMod = self._userType in typeGlobalModerator
            self._isGlobalMod = self.twitchAdmin or self._isGlobalMod
        return self._isGlobalMod
    
    def __getitem__(self, key: str) -> bool:
        if isinstance(key, str):
            if key == 'owner':
                return self.owner
            if key == 'manager':
                return self.manager
            if key in ['staff', 'twitchStaff']:
                return self.twitchStaff
            if key in ['admin', 'twitchAdmin']:
                return self.twitchAdmin
            if key in ['globalMod', 'globalModerator']:
                return self.globalModerator
            raise KeyError('unknown permission')
        raise TypeError('key is not of type str')
