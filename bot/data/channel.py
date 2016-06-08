from datetime import datetime
from source.api.bttv import getBroadcasterEmotes as getBttvEmotes
from source.api.ffz import getBroadcasterEmotes as getFfzEmotes
from typing import Any, Dict, Iterable, Optional, Set, Union
import bot.data.socket


class Channel:
    __slots__ = ['_channel', '_ircChannel', '_socket', '_isMod',
                 '_isSubscriber', '_ircUsers', '_ircOps', '_sessionData',
                 '_joinPriority', '_ffzEmotes', '_ffzCache', '_bttvEmotes',
                 '_bttvCache', '_twitchCache', '_streamingSince',
                 '_twitchStatus', '_twitchGame', '_serverCheck',
                 ]
    
    def __init__(self,
                 channel:str,
                 socket:bot.data.socket.Socket,
                 joinPriority:Union[int,float]=float('inf')) -> None:
        self._channel = channel  # type: str
        self._ircChannel = '#' + channel  # type: str
        self._socket = socket  # type: bot.data.socket.Socket
        self._isMod = False  # type: bool
        self._isSubscriber = False  # type: bool
        self._ircUsers = set()  # type: Set[str]
        self._ircOps = set()  # type: Set[str]
        self._joinPriority = float(joinPriority)  # type: float
        self._sessionData = {}  # type: Dict[Any, Any]
        self._ffzEmotes = {}  # type: Dict[int, str]
        self._ffzCache = datetime.min  # type: datetime
        self._bttvEmotes = {}  # type: Dict[str, str]
        self._bttvCache = datetime.min  # type: datetime
        self._twitchCache = datetime.min  # type: datetime
        self._streamingSince = None  # type: Optional[datetime]
        self._twitchStatus = None  # type: Optional[str]
        self._twitchGame = None  # type: Optional[str]
        self._serverCheck = None  # type: Optional[datetime]
    
    @property
    def channel(self) -> str:
        return self._channel
    
    @property
    def ircChannel(self) -> str:
        return self._ircChannel
    
    @property
    def socket(self) -> bot.data.socket.Socket:
        return self._socket
    
    @property
    def isMod(self) -> bool:
        return self._isMod
    
    @isMod.setter
    def isMod(self, value:bool) -> None:
        self._isMod = bool(value)
    
    @property
    def isSubscriber(self) -> bool:
        return self._isSubscriber
    
    @isSubscriber.setter
    def isSubscriber(self, value: bool) -> None:
        self._isSubscriber = bool(value)
    
    @property
    def ircUsers(self) -> Set[str]:
        return self._ircUsers
    
    @property
    def ircOps(self) -> Set[str]:
        return self._ircOps
    
    @property
    def joinPriority(self) -> float:
        return self._joinPriority
    
    @joinPriority.setter
    def joinPriority(self, value: Union[int,float]) -> None:
        self._joinPriority = float(value)
    
    @property
    def sessionData(self) -> Dict[Any, Any]:
        return self._sessionData
    
    @property
    def ffzCache(self) -> datetime:
        return self._ffzCache
    
    @property
    def ffzEmotes(self) -> Dict[int, str]:
        return self._ffzEmotes
    
    @property
    def bttvCache(self) -> datetime:
        return self._bttvCache
    
    @property
    def bttvEmotes(self) -> Dict[str,str]:
        return self._bttvEmotes
    
    @property
    def streamingSince(self) -> Optional[datetime]:
        return self._streamingSince
    
    @streamingSince.setter
    def streamingSince(self, value:Optional[datetime]) -> None:
        self._streamingSince = value
    
    @property
    def isStreaming(self) -> bool:
        return self._streamingSince is not None
    
    @property
    def twitchCache(self) -> datetime:
        return self._twitchCache
    
    @twitchCache.setter
    def twitchCache(self, value:datetime):
        self._twitchCache = value
    
    @property
    def twitchStatus(self) -> str:
        return self._twitchStatus
    
    @twitchStatus.setter
    def twitchStatus(self, value: str):
        self._twitchStatus = value
    
    @property
    def twitchGame(self) -> str:
        return self._twitchGame
    
    @twitchGame.setter
    def twitchGame(self, value: str):
        self._twitchGame = value
    
    @property
    def serverCheck(self) -> datetime:
        return self._serverCheck
    
    @serverCheck.setter
    def serverCheck(self, value:datetime):
        self._serverCheck = value
    
    def onJoin(self) -> None:
        self._ircUsers.clear()
        self._ircOps.clear()
    
    def part(self) -> None:
        self.socket.partChannel(self)
        self._socket.messaging.clearChat(self)
        self._socket = None
    
    def send(self,
             messages:Union[str,Iterable[str]],
             priority:int=1) -> None:
        self._socket.messaging.sendChat(self, messages, priority)
    
    def updateFfzEmotes(self) -> None:
        self._ffzCache = datetime.utcnow()
        emotes = getFfzEmotes(self._channel)
        self._ffzEmotes = emotes or self._ffzEmotes
    
    def updateBttvEmotes(self) -> None:
        self._bttvCache = datetime.utcnow()
        emotes = getBttvEmotes(self._channel)
        self._bttvEmotes = emotes or self._bttvEmotes
