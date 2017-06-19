import configparser
import os.path

import aioodbc
import aioodbc.cursor
import aiofiles
import pyodbc

from abc import ABCMeta, abstractmethod
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, Iterable, Mapping, NamedTuple, Optional
from typing import Sequence, Type, Union
from typing import AsyncIterator


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
    def __init__(self,
                 ini: Mapping[str, str],
                 **kwargs) -> None:
        self._engine: str
        self._connection: Any

    @property
    def engine(self) -> str:
        return self._engine

    @property
    def connection(self) -> Any:
        return self._connection

    @abstractmethod
    def connect(self) -> None:
        pass

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()

    def __enter__(self) -> 'DatabaseBase':
        self._connection = None
        self.connect()
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.close()

    @abstractmethod
    def getAutoJoinsChats(self) -> Iterable[AutoJoinChannel]:
        yield from []

    @abstractmethod
    def getAutoJoinsPriority(self, broadcaster: str) -> Union[int, float]:
        return float('inf')

    @abstractmethod
    def saveAutoJoin(self,
                     broadcaster: str,
                     priority: Union[int, float] = 0,
                     cluster: str = 'aws') -> bool:
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
                          cluster: str = 'aws') -> bool:
        return False

    @abstractmethod
    def getOAuthToken(self, broadcaster: str) -> Optional[str]:
        return None

    @abstractmethod
    def saveBroadcasterToken(self,
                             broadcaster: str,
                             token: str) -> None:
        pass

    @abstractmethod
    def getFullGameTitle(self, abbreviation: str) -> Optional[str]:
        return None

    @abstractmethod
    def getChatCommands(self,
                        broadcaster: str,
                        command: str) -> Dict[str, Dict[str, str]]:
        return {broadcaster: {}, '#global': {}}

    @abstractmethod
    def getCustomCommand(self,
                         broadcaster: str,
                         permission: str,
                         command: str) -> Optional[str]:
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
                             user: str) -> bool:
        return False

    @abstractmethod
    def appendCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            message: str,
                            user: str) -> bool:
        return False

    @abstractmethod
    def deleteCustomCommand(self,
                            broadcaster: str,
                            permission: str,
                            command: str,
                            user: str) -> bool:
        return False

    @abstractmethod
    def levelCustomCommand(self,
                           broadcaster: str,
                           permission: str,
                           command: str,
                           user: str,
                           new_permission: str) -> bool:
        return False

    @abstractmethod
    def renameCustomCommand(self,
                           broadcaster: str,
                           permission: str,
                           command: str,
                           user: str,
                           new_command: str) -> bool:
        return False

    @abstractmethod
    def getCustomCommandProperty(self,
                                 broadcaster: str,
                                 permission: str,
                                 command: str,
                                 property: Optional[CommandProperty]=None
                                 ) -> Optional[CommandReturn]:
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
                                     value: Optional[str]) -> bool:
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
                      length: Optional[int],
                      message: Optional[str],
                      reason: Optional[str]) -> bool:
        return False

    @abstractmethod
    def getChatProperty(self,
                        broadcaster: str,
                        property: str,
                        default: Any = None,
                        parse: Optional[Callable[[str], Any]] = None) -> Any:
        return default

    @abstractmethod
    def getChatProperties(self,
                          broadcaster: str,
                          properties: Sequence[str],
                          default: Any = None,
                          parse: Any = None) -> Mapping[str, Any]:
        return {}

    @abstractmethod
    def setChatProperty(self,
                        broadcaster: str,
                        property: str,
                        value: Optional[str] = None) -> bool:
        return False

    @abstractmethod
    def isPermittedUser(self,
                        broadcaster: str,
                        user: str) -> bool:
        return False

    @abstractmethod
    def addPermittedUser(self,
                         broadcaster: str,
                         user: str,
                         moderator: str) -> bool:
        return False

    @abstractmethod
    def removePermittedUser(self,
                            broadcaster: str,
                            user: str,
                            moderator: str) -> bool:
        return False

    @abstractmethod
    def isBotManager(self, user: str) -> bool:
        return False

    @abstractmethod
    def addBotManager(self, user: str) -> bool:
        return False

    @abstractmethod
    def removeBotManager(self, user: str) -> bool:
        return False

    @abstractmethod
    def getAutoRepeatToSend(self) -> Iterable[AutoRepeatMessage]:
        yield from []

    @abstractmethod
    def listAutoRepeat(self, broadcaster: str) -> Iterable[AutoRepeatList]:
        yield from []

    @abstractmethod
    def clearAutoRepeat(self, broadcaster: str) -> bool:
        return False

    @abstractmethod
    def sentAutoRepeat(self,
                       broadcaster: str,
                       name: str) -> bool:
        return False

    @abstractmethod
    def setAutoRepeat(self,
                      broadcaster: str,
                      name: str,
                      message: str,
                      count: Optional[int],
                      minutes: float) -> bool:
        return False

    @abstractmethod
    def removeAutoRepeat(self,
                         broadcaster: str,
                         name: str) -> bool:
        return False


class Schema(Enum):
    Main = 'file'
    OAuth = 'oauth'
    Timeout = 'timeoutlog'
    TimeZone = 'timezonedb'


class Database:
    def __init__(self,
                 connectionString: str,
                 **kwargs) -> None:
        self._connectionString: str = connectionString
        self._connection: Optional[aioodbc.Connection] = None

    @property
    def connection(self) -> Any:
        return self._connection

    async def connect(self) -> None:
        self._connection = await aioodbc.connect(dsn=self._connectionString)

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()

    async def __aenter__(self) -> 'Database':
        await self.connect()
        return self

    async def __aexit__(self, type, value, traceback) -> None:
        await self.close()

    async def cursor(self) -> aioodbc.cursor.Cursor:
        return await self.connection.cursor()


class DatabaseMain(Database):
    async def getAutoJoinsChats(self) -> AsyncIterator[AutoJoinChannel]:
        query: str = '''
SELECT broadcaster, priority, cluster FROM auto_join ORDER BY priority ASC
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            r: tuple
            await cursor.execute(query)
            async for r in cursor:
                yield AutoJoinChannel(*r)

    async def saveAutoJoin(self,
                           broadcaster: str,
                           priority: Union[int, float] = 0,
                           cluster: str = 'aws') -> bool:
        query: str = '''
INSERT INTO auto_join (broadcaster, priority, cluster) VALUES (?, ?, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                cursor.execute(query, (broadcaster, priority, cluster))
                self.connection.commit()
                return True
            except pyodbc.IntegrityError:
                return False


class DatabaseOAuth(Database):
    pass


class DatabaseTimeout(Database):
    pass


class DatabaseTimeZone(Database):
    pass


async def get_database(schema: Schema=Schema.Main) -> Database:
    databases: Dict[Schema, Type[Database]] = {
        Schema.Main: DatabaseMain,
        Schema.OAuth: DatabaseOAuth,
        Schema.Timeout: DatabaseTimeout,
        Schema.TimeZone: DatabaseTimeZone,
    }
    if os.path.isfile('config.ini'):
        ini: configparser.ConfigParser = configparser.ConfigParser()
        async with aiofiles.open('config.ini', 'r', encoding='utf-8') as file:
            ini.read_string(await file.read(None))
        return databases[schema](ini['DATABASE'][schema.value])
    raise ValueError()
