from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Dict, Iterable, Mapping, NamedTuple, Optional
from typing import Sequence, Union, overload

AutoJoinChannel = NamedTuple('AutoJoinChannel',
                             [('broadcaster', str),
                              ('priority', Union[int, float]),
                              ('cluster', str)])
CommandProperty = Union[str, Sequence[str]]
CommandReturn = Union[str, Dict[str, str]]



class DatabaseBase(metaclass=ABCMeta):
    def __init__(self, **kwargs) -> None: ...
    @property
    def engine(self) -> str: ...
    @property
    def connection(self) -> Any: ...
    def connect(self) -> None: ...
    def close(self) -> None: ...
    def __enter__(self) -> 'DatabaseBase': ...
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
    def getFullGameTitle(self, abbreviation: str) -> Optional[str]: ...
    @abstractmethod
    def getChatCommands(self,
                        broadcaster:str,
                        command:str) -> Dict[str, Dict[str, str]]: ...
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
            property: Optional[CommandProperty]=None) -> Optional[CommandReturn]: ...
    @abstractmethod
    def processCustomCommandProperty(self,
                                     broadcaster: str,
                                     permission: str,
                                     command: str,
                                     property: str,
                                     value: Optional[str]=None) -> bool: ...
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
                      length: Optional[int],
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
