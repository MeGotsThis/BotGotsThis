from . import AutoJoinChannel, CommandProperty, CommandReturn, DatabaseBase
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence
from typing import Union

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
            property: Optional[CommandProperty]=None) -> Optional[CommandReturn]:
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
                      length: Optional[int],
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
