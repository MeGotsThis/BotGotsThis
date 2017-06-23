import os.path

import aioodbc
import aioodbc.cursor
import pyodbc

import bot

from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Mapping
from typing import NamedTuple, Optional, Sequence, Tuple, Type, TypeVar, Union
from typing import overload

T = TypeVar('T')
S = TypeVar('S')


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


class Schema(Enum):
    Main = 'main'
    OAuth = 'oauth'
    Timeout = 'timeout'
    TimeZone = 'timezone'


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

    async def getAutoJoinsPriority(self, broadcaster: str) -> Union[int, float]:
        query: str = '''SELECT priority FROM auto_join WHERE broadcaster=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            autoJoinRow: Optional[Tuple[int]] = await cursor.fetchone()
            if autoJoinRow is not None:
                return int(autoJoinRow[0])
            else:
                return float('inf')

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
                await cursor.execute(query, (broadcaster, priority, cluster))
                await self.connection.commit()
                return True
            except pyodbc.Error:
                return False

    async def discardAutoJoin(self, broadcaster: str) -> bool:
        query: str = '''DELETE FROM auto_join WHERE broadcaster=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            await self.connection.commit()
            return cursor.rowcount != 0

    async def setAutoJoinPriority(self,
                                  broadcaster: str,
                                  priority: Union[int, float]) -> bool:
        query: str = '''UPDATE auto_join SET priority=? WHERE broadcaster=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (priority, broadcaster))
            await self.connection.commit()
            return cursor.rowcount != 0

    async def setAutoJoinServer(self,
                                broadcaster: str,
                                cluster: str = 'aws') -> bool:
        query: str = '''UPDATE auto_join SET cluster=? WHERE broadcaster=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (cluster, broadcaster))
            await self.connection.commit()
            return cursor.rowcount != 0

    async def getFullGameTitle(self, abbreviation: str) -> Optional[str]:
        query: str = '''
SELECT DISTINCT twitchGame
    FROM game_abbreviations
    WHERE abbreviation=?
        OR twitchGame=?
    ORDER BY twitchGame=? DESC
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (abbreviation, ) * 3)
            game: Optional[Tuple[str]] = await cursor.fetchone()
            return game and game[0]

    async def getChatCommands(self,
                              broadcaster: str,
                              command: str) -> Dict[str, Dict[str, str]]:
        query: str = '''
SELECT broadcaster, permission, fullMessage
    FROM custom_commands WHERE broadcaster IN (?, \'#global\') AND command=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            commands: Dict[str, Dict[str, str]]
            commands = {broadcaster: {}, '#global': {}}
            row: Optional[Tuple[str, str, str]]
            await cursor.execute(query, (broadcaster, command))
            async for row in cursor:
                commands[row[0]][row[1]] = row[2]
            return commands

    async def getCustomCommand(self,
                               broadcaster: str,
                               permission: str,
                               command: str) -> Optional[str]:
        find: str = '''
SELECT fullMessage FROM custom_commands
    WHERE broadcaster=? AND permission=? AND command=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(find, (broadcaster, permission,
                                        command.lower()))
            row: Optional[Tuple[str]] = await cursor.fetchone()
            return row and row[0]

    async def insertCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  fullMessage: str,
                                  user: str) -> bool:
        query: str = '''
INSERT INTO custom_commands
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created, lastEditor, lastUpdated)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                lower: str = command.lower()
                display: Optional[str] = None
                if lower != command:
                    display = command
                await cursor.execute(query, (broadcaster, permission, lower,
                                             display, fullMessage, user, user))
            except pyodbc.Error:
                return False

            await cursor.execute(history, (broadcaster, permission, lower,
                                           display, 'add', fullMessage, user))
            await self.connection.commit()
            return True

    async def updateCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  fullMessage: str,
                                  user: str) -> bool:
        query: str = '''
UPDATE custom_commands
    SET commandDisplay=?, fullMessage=?, lastEditor=?,
        lastUpdated=CURRENT_TIMESTAMP
    WHERE broadcaster=? AND permission=? AND command=?
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            display: Optional[str] = None
            if command.lower() != command:
                display = command
            await cursor.execute(query, (display, fullMessage, user,
                                         broadcaster, permission,
                                         command.lower()))
            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, permission,
                                           command.lower(), display, 'edit',
                                           fullMessage, user))
            await self.connection.commit()
            return True

    async def replaceCustomCommand(self,
                                   broadcaster: str,
                                   permission: str,
                                   command: str,
                                   fullMessage: str,
                                   user: str) -> bool:
        query: str = '''
REPLACE INTO custom_commands
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created, lastEditor, lastUpdated)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            display: Optional[str] = None
            if command.lower() != command:
                display = command
            await cursor.execute(query, (broadcaster, permission,
                                         command.lower(), display, fullMessage,
                                         user, user))
            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, permission,
                                           command.lower(), display, 'replace',
                                           fullMessage, user))
            await self.connection.commit()
            return True

    async def appendCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  message: str,
                                  user: str) -> bool:
        find: str = '''
SELECT fullMessage FROM custom_commands
    WHERE broadcaster=? AND permission=? AND command=?
'''
        query: str = '''
UPDATE custom_commands
    SET fullMessage=?, lastEditor=?, lastUpdated=CURRENT_TIMESTAMP
    WHERE broadcaster=? AND permission=? AND command=?
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(find, (broadcaster, permission,
                                        command.lower()))
            original: Optional[Tuple[str]] = await cursor.fetchone()
            if original is None:
                return False
            fullMessage: str = original[0] + message

            display: Optional[str] = None
            if command.lower() != command:
                display = command
            await cursor.execute(query, (fullMessage, user, broadcaster,
                                         permission, command.lower()))
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, permission,
                                           command.lower(), display, 'append',
                                           fullMessage, user))
            await self.connection.commit()
            return True

    async def deleteCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  user: str) -> bool:
        query: str = '''
DELETE FROM custom_commands
    WHERE broadcaster=? AND permission=? AND command=?
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, permission,
                                         command.lower()))

            if cursor.rowcount == 0:
                return False

            display: Optional[str] = None
            if command.lower() != command:
                display = command
            await cursor.execute(history, (broadcaster, permission,
                                           command.lower(), display, 'delete',
                                           None, user))
            await self.connection.commit()
            return True

    async def levelCustomCommand(self,
                                 broadcaster: str,
                                 permission: str,
                                 command: str,
                                 user: str,
                                 new_permission: str) -> bool:
        query: str = '''
UPDATE custom_commands SET permission=?
    WHERE broadcaster=? AND permission=? AND command=?
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                await cursor.execute(query, (new_permission, broadcaster,
                                             permission, command.lower()))
            except pyodbc.Error:
                return False

            if cursor.rowcount == 0:
                return False

            display: Optional[str] = None
            if command.lower() != command:
                display = command
            await cursor.execute(history, (broadcaster, new_permission,
                                           command.lower(), display, 'level',
                                           permission, user))
            await self.connection.commit()
            return True

    async def renameCustomCommand(self,
                                  broadcaster: str,
                                  permission: str,
                                  command: str,
                                  user: str,
                                  new_command: str) -> bool:
        query: str = '''
UPDATE custom_commands SET command=?, commandDisplay=?
    WHERE broadcaster=? AND permission=? AND command=?
'''
        history: str = '''
INSERT INTO custom_commands_history
    (broadcaster, permission, command, commandDisplay, process, fullMessage,
    creator, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            display: Optional[str] = None
            if new_command.lower() != new_command:
                display = new_command
            try:
                await cursor.execute(query, (new_command.lower(), display,
                                             broadcaster, permission,
                                             command.lower()))
            except pyodbc.Error:
                return False

            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, permission,
                                           new_command.lower(), display,
                                           'rename', command.lower(), user))
            await self.connection.commit()
            return True

    async def getCustomCommandProperty(
            self,
            broadcaster: str,
            permission: str,
            command: str,
            property: Optional[CommandProperty]=None
            ) -> Optional[CommandReturn]:
        query: str
        cursor: aioodbc.cursor.Cursor
        p: str
        v: str
        params: tuple
        values: Dict[str, str]
        async with await self.cursor() as cursor:
            if property is None:
                query = '''
SELECT property, value FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=?
'''
                values = {}
                params = (broadcaster, permission, command.lower())
                await cursor.execute(query, params)
                async for p, v in cursor:
                    values[p] = v
                return values
            elif isinstance(property, list):
                query = '''
SELECT property, value FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=?
        AND property IN (%s)
''' % ','.join('?' * len(property))
                values = {}
                params = (broadcaster, permission, command.lower(),
                                 ) + tuple(property)
                await cursor.execute(query, params)
                async for p, v in cursor:
                    values[p] = v
                for p in property:
                    if p not in values:
                        values[p] = None
                return values
            else:
                query = '''
SELECT value FROM custom_command_properties 
    WHERE broadcaster=? AND permission=? AND command=? AND property=?
'''
                await cursor.execute(query, (broadcaster, permission,
                                             command.lower(), property))
                row: Optional[Tuple[str]] = await cursor.fetchone()
                return row and row[0]

    async def processCustomCommandProperty(self,
                                           broadcaster: str,
                                           permission: str,
                                           command: str,
                                           property: str,
                                           value: Optional[str]=None) -> bool:
        query: str
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                if value is None:
                    query = '''
DELETE FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=? AND property=?
'''
                    await cursor.execute(query, (broadcaster, permission,
                                                 command.lower(), property))
                else:
                    query = '''
REPLACE INTO custom_command_properties
    (broadcaster, permission, command, property, value)
    VALUES (?, ?, ?, ?, ?)
'''
                    await cursor.execute(query, (broadcaster, permission,
                                                 command.lower(), property,
                                                 value))
                await self.connection.commit()
                return cursor.rowcount != 0
            except pyodbc.Error:
                return False

    async def hasFeature(self,
                         broadcaster: str,
                         feature: str) -> bool:
        query: str = '''
SELECT 1 FROM chat_features WHERE broadcaster=? AND feature=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, feature))
            return await cursor.fetchone() is not None

    async def addFeature(self,
                         broadcaster: str,
                         feature: str) -> bool:
        query: str = '''
INSERT INTO chat_features (broadcaster, feature) VALUES (?, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                await cursor.execute(query, (broadcaster, feature))
                await self.connection.commit()
                return True
            except pyodbc.Error:
                return False

    async def removeFeature(self,
                            broadcaster: str,
                            feature: str) -> bool:
        query: str = '''
DELETE FROM chat_features WHERE broadcaster=? AND feature=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, feature))
            await self.connection.commit()
            return cursor.rowcount != 0

    async def listBannedChannels(self) -> AsyncIterator[str]:
        query: str = '''SELECT broadcaster FROM banned_channels'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query)
            broadcaster: str
            async for broadcaster, in cursor:
                yield broadcaster

    async def isChannelBannedReason(self, broadcaster: str) -> Optional[str]:
        query: str = '''
SELECT reason FROM banned_channels WHERE broadcaster=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            row: Optional[Tuple[str]] = await cursor.fetchone()
            return row and row[0]

    async def addBannedChannel(self,
                               broadcaster: str,
                               reason: str,
                               nick: str) -> bool:
        query: str = '''
INSERT INTO banned_channels 
    (broadcaster, currentTime, reason, who)
    VALUES (?, CURRENT_TIMESTAMP, ?, ?)
'''
        history: str = '''
INSERT INTO banned_channels_log
    (broadcaster, currentTime, reason, who, actionLog) 
    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                await cursor.execute(query, (broadcaster, reason, nick))
            except pyodbc.Error:
                return False

            await cursor.execute(history, (broadcaster, reason, nick, 'add'))
            await self.connection.commit()
            return True

    async def removeBannedChannel(self,
                                  broadcaster: str,
                                  reason: str,
                                  nick: str) -> bool:
        query: str = '''
DELETE FROM banned_channels WHERE broadcaster=?
'''
        history: str = '''
INSERT INTO banned_channels_log
    (broadcaster, currentTime, reason, who, actionLog) 
    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, reason, nick,
                                           'remove'))
            await self.connection.commit()
            return True

    @overload
    async def getChatProperty(self,
                              broadcaster: str,
                              property: str) -> Optional[str]: ...
    @overload
    async def getChatProperty(self,
                              broadcaster: str,
                              property: str,
                              default: T
                              ) -> Union[str, T]: ...
    @overload
    async def getChatProperty(self,
                              broadcaster: str,
                              property: str,
                              default: T,
                              parse: Callable[[str], S]
                              ) -> Union[T, S]: ...
    async def getChatProperty(self,
                              broadcaster,
                              property,
                              default=None,
                              parse=None):
        query: str = '''
SELECT value FROM chat_properties WHERE broadcaster=? AND property=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, property,))
            row: Optional[Tuple[str]] = await cursor.fetchone()
            if row is None:
                return default
            if parse is not None:
                return parse(row[0])
            return row[0]

    @overload
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str]
                                ) -> Mapping[str, Optional[str]]: ...
    @overload
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: T
                                ) -> Mapping[str, Union[str, T]]: ...
    @overload
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: Mapping[str, T]
                                ) -> Mapping[str, Union[str, T]]: ...
    @overload
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: T,
                                parse: Mapping[str, Callable[[str], S]]
                                ) -> Mapping[str, Union[str, T, S]]: ...
    @overload
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: T,
                                parse: Callable[[str], S]
                                ) -> Mapping[str, Union[T, S]]: ...
    @overload
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: Mapping[str, T],
                                parse: Mapping[str, Callable[[str], S]]
                                ) -> Mapping[str, Union[str, T, S]]: ...
    @overload
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: Mapping[str, T],
                                parse: Callable[[str], S]
                                ) -> Mapping[str, Union[T, S]]: ...
    async def getChatProperties(self, broadcaster, properties, default=None,
                                parse=None):
        query: str = '''
SELECT property, value FROM chat_properties
    WHERE broadcaster=? AND property IN (%s)
''' % ','.join('?' * len(properties))
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            values: Dict[str, Any] = {}
            params = (broadcaster,) + tuple(properties)
            await cursor.execute(query, params)
            async for property, value in cursor:
                if isinstance(parse, dict) and property in parse:
                    value = parse[property](value)
                if callable(parse):
                    value = parse(value)
                values[property] = value
            for property in properties:
                if property not in values:
                    if isinstance(default, dict):
                        if property in default:
                            value = default[property]
                        else:
                            continue
                    else:
                        value = default
                    values[property] = value
            return values

    async def setChatProperty(self,
                              broadcaster: str,
                              property: str,
                              value: Optional[str]=None) -> bool:
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            query: str
            params: tuple
            if value is None:
                query = '''
DELETE FROM chat_properties WHERE broadcaster=? AND property=?
'''
                params = broadcaster, property,
            else:
                query = '''
REPLACE INTO chat_properties (broadcaster, property, value) VALUES (?, ?, ?)
'''
                params = broadcaster, property, value,
            await cursor.execute(query, params)
            await self.connection.commit()
            return cursor.rowcount != 0

    async def isPermittedUser(self,
                              broadcaster: str,
                              user: str) -> bool:
        query: str = '''
SELECT 1 FROM permitted_users WHERE broadcaster=? AND twitchUser=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, user,))
            return bool(await cursor.fetchone())

    async def addPermittedUser(self,
                               broadcaster: str,
                               user: str,
                               moderator: str) -> bool:
        query: str = '''
INSERT INTO permitted_users (broadcaster, twitchUser) VALUES (?, ?)
'''
        history: str = '''
INSERT INTO permitted_users_log
    (broadcaster, twitchUser, moderator, created, actionLog)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                await cursor.execute(query, (broadcaster, user))
            except pyodbc.Error:
                return False

            await cursor.execute(history, (broadcaster, user, moderator,
                                           'add'))
            await self.connection.commit()
            return True

    async def removePermittedUser(self,
                                  broadcaster: str,
                                  user: str,
                                  moderator: str) -> bool:
        query: str = '''
DELETE FROM permitted_users WHERE broadcaster=? AND twitchUser=?
'''
        history: str = '''
INSERT INTO permitted_users_log
    (broadcaster, twitchUser, moderator, created, actionLog)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, user))
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, user, moderator,
                                           'remove'))
            await self.connection.commit()
            return True

    async def isBotManager(self, user: str) -> bool:
        query: str = '''SELECT 1 FROM bot_managers WHERE twitchUser=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (user,))
            return bool(await cursor.fetchone())

    async def addBotManager(self, user: str) -> bool:
        query: str = '''
INSERT INTO bot_managers (twitchUser) VALUES (?)
'''
        history: str = '''
INSERT INTO bot_managers_log
    (twitchUser, created, actionLog)
    VALUES (?, CURRENT_TIMESTAMP, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                await cursor.execute(query, (user,))
            except pyodbc.Error:
                return False

            await cursor.execute(history, (user, 'add'))
            await self.connection.commit()
            return True

    async def removeBotManager(self, user: str) -> bool:
        query: str = '''
DELETE FROM bot_managers WHERE twitchUser=?
'''
        history: str = '''
INSERT INTO bot_managers_log
    (twitchUser, created, actionLog)
    VALUES (?, CURRENT_TIMESTAMP, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (user,))
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (user, 'remove'))
            await self.connection.commit()
            return True

    async def getAutoRepeatToSend(self) -> AsyncIterator[AutoRepeatMessage]:
        query: str = '''
SELECT broadcaster, name, message FROM auto_repeat
    WHERE datetime(lastSent, '+' || duration || ' minutes')
        <= CURRENT_TIMESTAMP'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query)
            async for broadcaster, name, message in cursor:
                yield AutoRepeatMessage(broadcaster, name, message)

    async def listAutoRepeat(self, broadcaster: str
                             ) -> AsyncIterator[AutoRepeatList]:
        query: str = '''
SELECT name, message, numLeft, duration, lastSent FROM auto_repeat
    WHERE broadcaster=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            row: tuple
            async for row in cursor:
                name: str
                message: str
                count: Optional[int]
                duration: float
                last: datetime
                name, message, count, duration, last = row
                yield AutoRepeatList(name, message, count, duration, last)

    async def clearAutoRepeat(self, broadcaster: str) -> bool:
        query: str = '''DELETE FROM auto_repeat WHERE broadcaster=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            await self.connection.commit()
            return cursor.rowcount != 0

    async def sentAutoRepeat(self,
                             broadcaster: str,
                             name: str) -> bool:
        query: str = '''
UPDATE auto_repeat SET numLeft=numLeft-1, lastSent=CURRENT_TIMESTAMP
    WHERE broadcaster=? AND name=?
'''
        delete: str = '''
DELETE FROM auto_repeat
    WHERE broadcaster=? AND name=? AND numLeft IS NOT NULL AND numLeft<=0
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, name))
            ret: bool = cursor.rowcount != 0
            await cursor.execute(delete, (broadcaster, name))
            await self.connection.commit()
            return ret

    async def setAutoRepeat(self,
                            broadcaster: str,
                            name: str,
                            message: str,
                            count: Optional[int],
                            minutes: float) -> bool:
        query: str = '''
REPLACE INTO auto_repeat
    (broadcaster, name, message, numLeft, duration, lastSent)
VALUES (?, ?, ?, ?, ?, datetime('now', '-' || ? || ' minutes'))'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, name, message, count,
                                         minutes, minutes))
            await self.connection.commit()
            return cursor.rowcount != 0

    async def removeAutoRepeat(self,
                               broadcaster: str,
                               name: str) -> bool:
        query: str = '''
DELETE FROM auto_repeat WHERE broadcaster=? AND name=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, name))
            await self.connection.commit()
            return cursor.rowcount != 0


class DatabaseOAuth(Database):
    async def getOAuthToken(self, broadcaster: str) -> Optional[str]:
        query: str = 'SELECT token FROM oauth_tokens WHERE broadcaster=?'
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            token: Optional[Tuple[str]] = await cursor.fetchone()
            return token and token[0]

    async def saveBroadcasterToken(self,
                                   broadcaster: str,
                                   token: str) -> None:
        query: str = '''
REPLACE INTO oauth_tokens (broadcaster, token) VALUES (?, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, token))
            await self.connection.commit()


class DatabaseTimeout(Database):
    async def recordTimeout(self,
                            broadcaster: str,
                            user: str,
                            fromUser: Optional[str],
                            module: str,
                            level: Optional[int],
                            length: Optional[int],
                            message: Optional[str],
                            reason: Optional[str]) -> bool:
        query: str = '''
INSERT INTO timeout_logs 
    (broadcaster, twitchUser, fromUser, module, level, length, message, reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                await cursor.execute(query, (broadcaster, user, fromUser,
                                             module, level, length, message,
                                             reason))
                await self.connection.commit()
                return True
            except pyodbc.Error:
                return False


class DatabaseTimeZone(Database):
    async def timezone_names(self) -> AsyncIterator[Tuple[str, int]]:
        '''
        For the abbreviation conflicts of: CST, CDT, AMT, AST, GST, IST,
        KST, BST
        I have choosen: America/Chicago, America/Boa_Vista,
        America/Puerto_Rico, Asia/Muscat, Asia/Jerusalem, Asia/Seoul,
        Europe/London
        '''
        query: str = '''
SELECT abbreviation, gmt_offset
    FROM timezone
    WHERE time_start >= 2114380800
        AND abbreviation NOT IN ('CST', 'CDT', 'AMT', 'AST', 'GST', 'IST',
                                 'KST', 'BST', 'UTC')
    GROUP BY abbreviation
UNION ALL
SELECT abbreviation, gmt_offset
    FROM timezone
    WHERE time_start=2147483647
        AND zone_id IN (382, 75, 294, 281, 190, 211, 159)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query)
            async for row in cursor:
                yield row[0], row[1]

    async def zones(self) -> AsyncIterator[Tuple[str, int]]:
            query: str = '''
SELECT zone_id, zone_name FROM zone ORDER BY zone_id
'''
            cursor: aioodbc.cursor.Cursor
            async with await self.cursor() as cursor:
                await cursor.execute(query)
                async for row in cursor:
                    yield row[0], row[1]

    async def zone_transitions(self) -> List[Tuple[int, str, int, int]]:
        query: str = '''
SELECT zone_id, abbreviation, time_start, gmt_offset 
    FROM timezone
    WHERE abbreviation != 'UTC' 
    ORDER BY zone_id, time_start
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query)
            return [tuple(row) for row in await cursor.fetchall()]


def get_database(schema: Schema=Schema.Main) -> Database:
    databases: Dict[Schema, Type[Database]] = {
        Schema.Main: DatabaseMain,
        Schema.OAuth: DatabaseOAuth,
        Schema.Timeout: DatabaseTimeout,
        Schema.TimeZone: DatabaseTimeZone,
    }
    if schema in databases and schema.value in bot.config.database:
        return databases[schema](bot.config.database[schema.value])
    raise ValueError()
