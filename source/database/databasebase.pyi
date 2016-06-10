from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence
from typing import Union, overload
from ..data.return_ import AutoJoinChannel


class DatabaseBase(metaclass=ABCMeta):
    __slots__ = ()
    def __init__(self, **kwargs) -> None: ...
    @property
    def engine(self) -> str: ...
    @property
    def connection(self) -> Any: ...
    def __enter__(self) -> Any: ...
    def __exit__(self, type, value, traceback) -> None: ...
    @abstractmethod
    def getAutoJoinsChats(self) -> Iterable[AutoJoinChannel]: ...
    @abstractmethod
    def getAutoJoinsPriority(self, broadcaster: str) -> Union[int, float]: ...
    @abstractmethod
    def saveAutoJoin(self,
                     broadcaster: str,
                     priority: Union[int, float]=0,
                     cluster: str='aws') -> bool: ...
    @abstractmethod
    def discardAutoJoin(self, broadcaster: str) -> bool: ...
    @abstractmethod
    def setAutoJoinPriority(self,
                            broadcaster: str,
                            priority: Union[int, float]) -> bool: ...
    @abstractmethod
    def setAutoJoinServer(self,
                          broadcaster: str,
                          cluster:str='aws') -> bool: ...
    @abstractmethod
    def getOAuthToken(self, broadcaster:str) -> Optional[str]: ...
    @abstractmethod
    def saveBroadcasterToken(self,
                             broadcaster:str,
                             token:str) -> None: ...
    @abstractmethod
    def getChatCommands(self,
                        broadcaster:str,
                        command:str) -> Dict[str, Dict[str, str]]: ...
    @abstractmethod
    def getFullGameTitle(self, abbreviation: str) -> Optional[str]: ...
    @abstractmethod
    def insertCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            fullMessage: str,
                            user: str) -> bool: ...
    @abstractmethod
    def updateCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            fullMessage: str,
                            user: str) -> bool: ...
    @abstractmethod
    def replaceCustomCommand(self,
                             broadcaster: str,
                             permission: str,
                             command: str,
                             fullMessage: str,
                             user: str): ...
    @abstractmethod
    def appendCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            message: str,
                            user: str): ...
    @abstractmethod
    def deleteCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            user: str): ...
    @abstractmethod
    def getCustomCommandProperty(
            self,
            broadcaster: str,
            permission: str,
            command: str,
            property: Optional[Union[str, Sequence[str]]]=None) -> Optional[Union[str, Dict[str, str]]]: ...
    @abstractmethod
    def processCustomCommandProperty(self,
                                     broadcaster: str,
                                     permission: str,
                                     command: str,
                                     property: str,
                                     value=Optional[str]) -> bool: ...
    @abstractmethod
    def hasFeature(self,
                   broadcaster: str,
                   feature: str) -> bool: ...
    @abstractmethod
    def addFeature(self,
                   broadcaster: str,
                   feature: str) -> bool: ...
    @abstractmethod
    def removeFeature(self,
                      broadcaster: str,
                      feature: str) -> bool: ...
    @abstractmethod
    def listBannedChannels(self) -> Iterable[str]: ...
    @abstractmethod
    def isChannelBannedReason(self, broadcaster: str) -> Optional[str]: ...
    @abstractmethod
    def addBannedChannel(self,
                         broadcaster: str,
                         reason: str,
                         nick: str) -> bool: ...
    @abstractmethod
    def removeBannedChannel(self,
                            broadcaster: str,
                            reason: str,
                            nick: str) -> bool: ...
    @abstractmethod
    def recordTimeout(self,
                      broadcaster: str,
                      user: str,
                      fromUser: Optional[str],
                      module: str,
                      level: Optional[int],
                      length: int,
                      message: Optional[str],
                      reason: Optional[str]) -> bool: ...
    @abstractmethod
    def getChatProperty(self,
                        broadcaster: str,
                        property: str,
                        default: Any,
                        parse: Callable[[str], Any]=None) -> Any: ...
    @overload
    @abstractmethod
    def getChatProperties(self,
                          broadcaster: str,
                          properties: Sequence[str],
                          default: Any=None,
                          parse: Mapping[str, Any]=None) -> Mapping[str, Any]: ...
    @overload
    @abstractmethod
    def getChatProperties(self,
                          broadcaster: str,
                          properties: Sequence[str],
                          default: Any,
                          parse: Callable[[str], Any]) -> Mapping[str, Any]: ...
    @abstractmethod
    def setChatProperty(self,
                        broadcaster: str,
                        property: str,
                        value: str=None) -> bool: ...


class DatabaseNone(DatabaseBase):
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
    def getChatCommands(self,
                        broadcaster:str,
                        command:str) -> Dict[str, Dict[str, str]]: ...
    def getFullGameTitle(self, abbreviation: str) -> Optional[str]: ...
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
                             user: str): ...
    def appendCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            message: str,
                            user: str): ...
    def deleteCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            user: str): ...
    def getCustomCommandProperty(
            self,
            broadcaster: str,
            permission: str,
            command: str,
            property: Optional[Union[str, Sequence[str]]]=None) -> Optional[Union[str, Dict[str, str]]]: ...
    def processCustomCommandProperty(self,
                                     broadcaster: str,
                                     permission: str,
                                     command: str,
                                     property: str,
                                     value=Optional[str]) -> bool: ...
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
                      length: int,
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
                          parse: Mapping[str, Any]=None) -> Mapping[str, Any]: ...
    @overload
    def getChatProperties(self,
                          broadcaster: str,
                          properties: Sequence[str],
                          default: Any,
                          parse: Callable[[str], Any]) -> Mapping[str, Any]: ...
    def setChatProperty(self,
                        broadcaster: str,
                        property: str,
                        value: str=None) -> bool: ...
