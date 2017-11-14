from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Set, Union

from bot import utils
from bot.coroutine import connection as connectionM
from lib.api import bttv


class Channel:
    __slots__ = ['_channel', '_ircChannel', '_connection', '_isMod',
                 '_isSubscriber', '_ircUsers', '_ircOps', '_sessionData',
                 '_joinPriority',
                 '_bttvEmotes', '_bttvCache', '_twitchCache', '_bttvLock',
                 '_streamingSince', '_twitchStatus', '_twitchGame',
                 '_community', '_serverCheck',
                 ]

    def __init__(self,
                 channel: str,
                 connection: 'connectionM.ConnectionHandler',
                 joinPriority: Union[int, float, str]=float('inf')) -> None:
        if not isinstance(channel, str):
            raise TypeError()
        if not isinstance(connection, connectionM.ConnectionHandler):
            raise TypeError()
        if not channel:
            raise ValueError()
        self._channel: str = channel
        self._ircChannel: str = '#' + channel
        self._connection: connectionM.ConnectionHandler = connection
        self._isMod: bool = False
        self._isSubscriber: bool = False
        self._ircUsers: Set[str] = set()
        self._ircOps: Set[str] = set()
        self._joinPriority: float = float(joinPriority)
        self._sessionData: Dict[Any, Any] = {}
        self._bttvEmotes: Dict[str, str] = {}
        self._bttvCache: datetime = datetime.min
        self._twitchCache: datetime = datetime.min
        self._streamingSince: Optional[datetime] = None
        self._twitchStatus: Optional[str] = ''
        self._twitchGame: Optional[str] = ''
        self._community: List[str] = []
        self._serverCheck: datetime = datetime.min

    @property
    def channel(self) -> str:
        return self._channel

    @property
    def ircChannel(self) -> str:
        return self._ircChannel

    @property
    def connection(self) -> 'connectionM.ConnectionHandler':
        return self._connection

    @property
    def isMod(self) -> bool:
        return self._isMod

    @isMod.setter
    def isMod(self, value: bool) -> None:
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
    def joinPriority(self, value: Union[int, float, str]) -> None:
        self._joinPriority = float(value)

    @property
    def sessionData(self) -> Dict[Any, Any]:
        return self._sessionData

    @property
    def bttvCache(self) -> datetime:
        return self._bttvCache

    @property
    def bttvEmotes(self) -> Dict[str, str]:
        return self._bttvEmotes

    @property
    def streamingSince(self) -> Optional[datetime]:
        return self._streamingSince

    @streamingSince.setter
    def streamingSince(self, value: Optional[datetime]) -> None:
        if value is not None and not isinstance(value, datetime):
            raise TypeError()
        self._streamingSince = value

    @property
    def isStreaming(self) -> bool:
        return self._streamingSince is not None

    @property
    def twitchCache(self) -> datetime:
        return self._twitchCache

    @twitchCache.setter
    def twitchCache(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError()
        self._twitchCache = value

    @property
    def twitchStatus(self) -> Optional[str]:
        return self._twitchStatus

    @twitchStatus.setter
    def twitchStatus(self, value: Optional[str]) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError()
        self._twitchStatus = value

    @property
    def twitchGame(self) -> Optional[str]:
        return self._twitchGame

    @twitchGame.setter
    def twitchGame(self, value: Optional[str]) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError()
        self._twitchGame = value

    @property
    def community(self) -> List[str]:
        return self._community

    @community.setter
    def community(self, value: List[str]) -> None:
        if not isinstance(value, list):
            raise TypeError()
        self._community = value[:]

    @property
    def serverCheck(self) -> datetime:
        return self._serverCheck

    @serverCheck.setter
    def serverCheck(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError()
        self._serverCheck = value

    def onJoin(self) -> None:
        self._ircUsers.clear()
        self._ircOps.clear()

    def part(self) -> None:
        self.connection.part_channel(self)
        self.connection.messaging.clearChat(self)

    def send(self,
             messages: Union[str, Iterable[str]],
             priority: int=1) -> None:
        self.connection.messaging.sendChat(self, messages, priority)

    def clear(self) -> None:
        self.connection.messaging.clearChat(self)

    async def updateBttvEmotes(self) -> None:
        oldTimestamp: datetime
        oldTimestamp, self._bttvCache = self._bttvCache, utils.now()
        emotes: Optional[Dict[str, str]]
        emotes = await bttv.getBroadcasterEmotes(self._channel)
        if emotes is not None:
            self._bttvEmotes = emotes
            self._bttvCache = utils.now()
        else:
            self._bttvCache = oldTimestamp
