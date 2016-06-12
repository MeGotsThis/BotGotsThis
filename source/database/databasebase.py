from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Dict, Iterable, Mapping, NamedTuple, Optional
from typing import Sequence, Union

AutoJoinChannel = NamedTuple('AutoJoinChannel',
                             [('broadcaster', str),
                              ('priority', Union[int, float]),
                              ('cluster', str)])



class DatabaseBase(metaclass=ABCMeta):
    def __init__(self, **kwargs) -> None:
        self._engine = 'None'  # type: str
        self._connection = None  # type: Any
    
    @property
    def engine(self) -> str:
        return self._engine
    
    @property
    def connection(self) -> Any:
        return self._connection
    
    def __enter__(self) -> Any:
        self._connection = None
        return self
    
    def __exit__(self, type, value, traceback) -> None:
        if self.connection is not None:
            self.connection.close()
    
    @abstractmethod
    def getAutoJoinsChats(self) -> Iterable[AutoJoinChannel]:
        yield from []
    
    @abstractmethod
    def getAutoJoinsPriority(self, broadcaster: str) -> Union[int, float]:
        return float('inf')
    
    @abstractmethod
    def saveAutoJoin(self,
                     broadcaster: str,
                     priority: Union[int, float]=0,
                     cluster: str='aws') -> bool:
        return False
    
    @abstractmethod
    def discardAutoJoin(self, broadcaster: str) -> bool:
        return False
    
    @abstractmethod
    def setAutoJoinPriority(self,
                            broadcaster: str,
                            priority: Union[int, float]) -> bool:
        return False
    
    @abstractmethod
    def setAutoJoinServer(self,
                          broadcaster: str,
                          cluster:str='aws') -> bool:
        return False
    
    @abstractmethod
    def getOAuthToken(self, broadcaster:str) -> Optional[str]:
        return None
    
    @abstractmethod
    def saveBroadcasterToken(self,
                             broadcaster:str,
                             token:str) -> None:
        pass
    
    @abstractmethod
    def getChatCommands(self,
                        broadcaster:str,
                        command:str) -> Dict[str, Dict[str, str]]:
        return {broadcaster: {}, '#global': {}}
    
    @abstractmethod
    def getFullGameTitle(self, abbreviation: str) -> Optional[str]:
        return None
    
    @abstractmethod
    def insertCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            fullMessage: str,
                            user: str) -> bool:
        return False
    
    @abstractmethod
    def updateCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            fullMessage: str,
                            user: str) -> bool:
        return False
    
    @abstractmethod
    def replaceCustomCommand(self,
                             broadcaster: str,
                             permission: str,
                             command: str,
                             fullMessage: str,
                             user: str):
        return False
    
    @abstractmethod
    def appendCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            message: str,
                            user: str):
        return False
    
    @abstractmethod
    def deleteCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            user: str):
        return True
    
    @abstractmethod
    def getCustomCommandProperty(
            self,
            broadcaster: str,
            permission: str,
            command: str,
            property: Optional[Union[str, Sequence[str]]]=None) -> Optional[Union[str, Dict[str, str]]]:
        if property is None:
            return {}
        elif isinstance(property, list):
            return {p: None for p in property}
        else:
            return None
    
    @abstractmethod
    def processCustomCommandProperty(self,
                                     broadcaster: str,
                                     permission: str,
                                     command: str,
                                     property: str,
                                     value=Optional[str]) -> bool:
        return False
    
    @abstractmethod
    def hasFeature(self,
                   broadcaster: str,
                   feature: str) -> bool:
        return False
    
    @abstractmethod
    def addFeature(self,
                   broadcaster: str,
                   feature: str) -> bool:
        return False
    
    @abstractmethod
    def removeFeature(self,
                      broadcaster: str,
                      feature: str) -> bool:
        return True
    
    @abstractmethod
    def listBannedChannels(self) -> Iterable[str]:
        yield from []
    
    @abstractmethod
    def isChannelBannedReason(self, broadcaster: str) -> Optional[str]:
        return None
    
    @abstractmethod
    def addBannedChannel(self,
                         broadcaster: str,
                         reason: str,
                         nick: str) -> bool:
        return True
    
    @abstractmethod
    def removeBannedChannel(self,
                            broadcaster: str,
                            reason: str,
                            nick: str) -> bool:
        return True
    
    @abstractmethod
    def recordTimeout(self,
                      broadcaster: str,
                      user: str,
                      fromUser: Optional[str],
                      module: str,
                      level: Optional[int],
                      length: int,
                      message: Optional[str],
                      reason: Optional[str]) -> bool:
        return False
    
    @abstractmethod
    def getChatProperty(self,
                        broadcaster: str,
                        property: str,
                        default: Any=None,
                        parse: Optional[Callable[[str], Any]]=None) -> Any:
        return default
    
    @abstractmethod
    def getChatProperties(self,
                          broadcaster: str,
                          properties: Sequence[str],
                          default: Any=None,
                          parse: Any=None) -> Mapping[str, Any]:
        return {}
    
    @abstractmethod
    def setChatProperty(self,
                        broadcaster: str,
                        property: str,
                        value: Optional[str]=None) -> bool:
        return False


class DatabaseNone(DatabaseBase):
    def getAutoJoinsChats(self) -> Iterable[AutoJoinChannel]:
        yield from []

    def getAutoJoinsPriority(self, broadcaster: str) -> Union[int, float]:
        return float('inf')

    def saveAutoJoin(self,
                     broadcaster: str,
                     priority: Union[int, float]=0,
                     cluster: str='aws') -> bool:
        return False

    def discardAutoJoin(self, broadcaster: str) -> bool:
        return False

    def setAutoJoinPriority(self,
                            broadcaster: str,
                            priority: Union[int, float]) -> bool:
        return False

    def setAutoJoinServer(self,
                          broadcaster: str,
                          cluster: str='aws') -> bool:
        return False

    def getOAuthToken(self, broadcaster: str) -> Optional[str]:
        return None

    def saveBroadcasterToken(self,
                             broadcaster: str,
                             token: str) -> None:
        pass

    def getChatCommands(self,
                        broadcaster: str,
                        command: str) -> Dict[str, Dict[str, str]]:
        return {broadcaster: {}, '#global': {}}

    def getFullGameTitle(self, abbreviation: str) -> Optional[str]:
        return None

    def insertCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            fullMessage: str,
                            user: str) -> bool:
        return False

    def updateCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            fullMessage: str,
                            user: str) -> bool:
        return False

    def replaceCustomCommand(self,
                             broadcaster: str,
                             permission: str,
                             command: str,
                             fullMessage: str,
                             user: str):
        return False

    def appendCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            message: str,
                            user: str):
        return False

    def deleteCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            user: str):
        return True

    def getCustomCommandProperty(
            self,
            broadcaster: str,
            permission: str,
            command: str,
            property: Optional[Union[str, Sequence[str]]]=None) -> Optional[Union[str, Dict[str, str]]]:
        if property is None:
            return {}
        elif isinstance(property, list):
            return {p: None for p in property}
        else:
            return None

    def processCustomCommandProperty(self,
                                     broadcaster: str,
                                     permission: str,
                                     command: str,
                                     property: str,
                                     value=Optional[str]) -> bool:
        return False

    def hasFeature(self,
                   broadcaster: str,
                   feature: str) -> bool:
        return False

    def addFeature(self,
                   broadcaster: str,
                   feature: str) -> bool:
        return False

    def removeFeature(self,
                      broadcaster: str,
                      feature: str) -> bool:
        return True

    def listBannedChannels(self) -> Iterable[str]:
        yield from []

    def isChannelBannedReason(self, broadcaster: str) -> Optional[str]:
        return None

    def addBannedChannel(self,
                         broadcaster: str,
                         reason: str,
                         nick: str) -> bool:
        return True

    def removeBannedChannel(self,
                            broadcaster: str,
                            reason: str,
                            nick: str) -> bool:
        return True

    def recordTimeout(self,
                      broadcaster: str,
                      user: str,
                      fromUser: Optional[str],
                      module: str,
                      level: Optional[int],
                      length: int,
                      message: Optional[str],
                      reason: Optional[str]) -> bool:
        return False

    def getChatProperty(self,
                        broadcaster: str,
                        property: str,
                        default: Any=None,
                        parse: Optional[Callable[[str], Any]]=None) -> Any:
        return default

    def getChatProperties(self,
                          broadcaster: str,
                          properties: Sequence[str],
                          default: Any=None,
                          parse: Any=None) -> Mapping[str, Any]:
        return {}

    def setChatProperty(self,
                        broadcaster: str,
                        property: str,
                        value: Optional[str]=None) -> bool:
        return False
