from abc import ABCMeta
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, Mapping, NamedTuple, Optional
from typing import Sequence, Union, overload

class AutoJoinChannel(NamedTuple):
    broadcaster: str
    priority: Union[int, float]
    cluster: str


class AutoRepeatMessage(NamedTuple):
    broadcaster: str
    name: str
    message: str


class AutoRepeatList(NamedTuple):
    name: str
    message: str
    count: Optional[int]
    duration: float
    last: datetime


CommandProperty = Union[str, Sequence[str]]
CommandReturn = Union[str, Dict[str, str]]



class DatabaseBase(metaclass=ABCMeta):
    def __init__(self, ini: Mapping[str, str], **kwargs) -> None: ...
    @property
    def engine(self) -> str: ...
    @property
    def connection(self) -> Any: ...
    def connect(self) -> None: ...
    def close(self) -> None: ...
    def __enter__(self) -> 'DatabaseBase': ...
    def __exit__(self, type, value, traceback) -> None: ...
    def getAutoJoinsChats(self) -> Iterable[AutoJoinChannel]: ...
    def getAutoJoinsPriority(self, broadcaster: str) -> Union[int, float]: ...
    def saveAutoJoin(self,
                     broadcaster: str,
                     priority: Union[int, float]=0,
                     cluster: str='aws') -> bool: ...
    def discardAutoJoin(self, broadcaster: str) -> bool: ...
    def setAutoJoinPriority(self,
                            broadcaster: str,
                            priority: Union[int, float]) -> bool: ...
    def setAutoJoinServer(self,
                          broadcaster: str,
                          cluster:str='aws') -> bool: ...
    def getOAuthToken(self, broadcaster:str) -> Optional[str]: ...
    def saveBroadcasterToken(self,
                             broadcaster:str,
                             token:str) -> None: ...
    def getFullGameTitle(self, abbreviation: str) -> Optional[str]: ...
    def getChatCommands(self,
                        broadcaster:str,
                        command:str) -> Dict[str, Dict[str, str]]: ...
    def getCustomCommand(self,
                         broadcaster: str,
                         permission: str,
                         command: str) -> Optional[str]: ...
    def insertCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            fullMessage: str,
                            user: str) -> bool: ...
    def updateCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            fullMessage: str,
                            user: str) -> bool: ...
    def replaceCustomCommand(self,
                             broadcaster: str,
                             permission: str,
                             command: str,
                             fullMessage: str,
                             user: str) -> bool: ...
    def appendCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            message: str,
                            user: str) -> bool: ...
    def deleteCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            user: str) -> bool: ...
    def levelCustomCommand(self,
                           broadcaster: str,
                           permission: str,
                           command: str,
                           user: str,
                           new_permission: str) -> bool: ...
    def renameCustomCommand(self,
                           broadcaster: str,
                           permission: str,
                           command: str,
                           user: str,
                           new_command: str) -> bool: ...
    def getCustomCommandProperty(self,
                                 broadcaster: str,
                                 permission: str,
                                 command: str,
                                 property: Optional[CommandProperty]=None
                                 ) -> Optional[CommandReturn]: ...
    def processCustomCommandProperty(self,
                                     broadcaster: str,
                                     permission: str,
                                     command: str,
                                     property: str,
                                     value: Optional[str]=None) -> bool: ...
    def hasFeature(self,
                   broadcaster: str,
                   feature: str) -> bool: ...
    def addFeature(self,
                   broadcaster: str,
                   feature: str) -> bool: ...
    def removeFeature(self,
                      broadcaster: str,
                      feature: str) -> bool: ...
    def listBannedChannels(self) -> Iterable[str]: ...
    def isChannelBannedReason(self, broadcaster: str) -> Optional[str]: ...
    def addBannedChannel(self,
                         broadcaster: str,
                         reason: str,
                         nick: str) -> bool: ...
    def removeBannedChannel(self,
                            broadcaster: str,
                            reason: str,
                            nick: str) -> bool: ...
    def recordTimeout(self,
                      broadcaster: str,
                      user: str,
                      fromUser: Optional[str],
                      module: str,
                      level: Optional[int],
                      length: Optional[int],
                      message: Optional[str],
                      reason: Optional[str]) -> bool: ...
    def getChatProperty(self,
                        broadcaster: str,
                        property: str,
                        default: Any,
                        parse: Callable[[str], Any]=None) -> Any: ...
    @overload
    def getChatProperties(self,
                          broadcaster: str,
                          properties: Sequence[str],
                          default: Any=None,
                          parse: Mapping[str, Any]=None
                          ) -> Mapping[str, Any]: ...
    @overload
    def getChatProperties(self,
                          broadcaster: str,
                          properties: Sequence[str],
                          default: Any,
                          parse: Callable[[str], Any]
                          ) -> Mapping[str, Any]: ...
    def setChatProperty(self,
                        broadcaster: str,
                        property: str,
                        value: str=None) -> bool: ...
    def isPermittedUser(self,
                        broadcaster: str,
                        user: str) -> bool: ...
    def addPermittedUser(self,
                         broadcaster: str,
                         user: str,
                         moderator: str) -> bool: ...
    def removePermittedUser(self,
                            broadcaster: str,
                            user: str,
                            moderator: str) -> bool: ...
    def isBotManager(self, user: str) -> bool: ...
    def addBotManager(self, user: str) -> bool: ...
    def removeBotManager(self, user: str) -> bool: ...
    def getAutoRepeatToSend(self) -> Iterable[AutoRepeatMessage]: ...
    def listAutoRepeat(self, broadcaster: str) -> Iterable[AutoRepeatList]: ...
    def clearAutoRepeat(self, broadcaster: str) -> bool: ...
    def sentAutoRepeat(self,
                       broadcaster: str,
                       name: str) -> bool: ...
    def setAutoRepeat(self,
                      broadcaster: str,
                      name: str,
                      message: str,
                      count: Optional[int],
                      minutes: float) -> bool: ...
    def removeAutoRepeat(self,
                         broadcaster: str,
                         name: str) -> bool: ...
