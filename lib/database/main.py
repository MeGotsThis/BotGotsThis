import aioodbc.cursor  # noqa: F401
import pyodbc

from datetime import datetime
from typing import Any, AsyncIterator, Callable, Dict, Mapping, NamedTuple  # noqa: F401,E501
from typing import Optional, Sequence, Set, Tuple, TypeVar, Union  # noqa: F401
from typing import overload

from ._base import Database

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
    remaining: Optional[int]
    duration: float
    last: datetime


CommandProperty = Union[str, Sequence[str]]
CommandReturn = Union[str, Dict[str, str]]


class DatabaseMain(Database):
    def __init__(self,
                 pool: aioodbc.Pool) -> None:
        super().__init__(pool)
        self.features: Optional[Set[str]] = None

    async def getAutoJoinsChats(self) -> AsyncIterator[AutoJoinChannel]:
        query: str = '''
SELECT broadcaster, priority, cluster FROM auto_join ORDER BY priority ASC
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            r: Tuple[Any, ...]
            async for r in await cursor.execute(query):
                yield AutoJoinChannel(*r)

    async def getAutoJoinsPriority(self, broadcaster: str
                                   ) -> Union[int, float]:
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
                await self.commit()
                return True
            except pyodbc.Error:
                return False

    async def discardAutoJoin(self, broadcaster: str) -> bool:
        query: str = '''DELETE FROM auto_join WHERE broadcaster=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            await self.commit()
            return cursor.rowcount != 0

    async def setAutoJoinPriority(self,
                                  broadcaster: str,
                                  priority: Union[int, float]) -> bool:
        query: str = '''UPDATE auto_join SET priority=? WHERE broadcaster=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (priority, broadcaster))
            await self.commit()
            return cursor.rowcount != 0

    async def setAutoJoinServer(self,
                                broadcaster: str,
                                cluster: str = 'aws') -> bool:
        query: str = '''UPDATE auto_join SET cluster=? WHERE broadcaster=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (cluster, broadcaster))
            await self.commit()
            return cursor.rowcount != 0

    async def getFullGameTitle(self, abbreviation: str) -> Optional[str]:
        query: str = '''
SELECT DISTINCT twitchGame, LOWER(twitchGame)=? AS isGame
    FROM game_abbreviations
    WHERE LOWER(abbreviation)=?
        OR LOWER(twitchGame)=?
    ORDER BY isGame DESC
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (abbreviation.lower(), ) * 3)
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
            params: Tuple[Any, ...] = (broadcaster, command)
            row: Optional[Tuple[str, str, str]]
            async for row in await cursor.execute(query, params):
                commands[row[0]][row[1]] = row[2]
            return commands

    async def getCustomCommands(self, broadcaster: str
                                ) -> AsyncIterator[Tuple[str, str, str]]:
        query: str = '''
SELECT command, permission, fullMessage FROM custom_commands
    WHERE broadcaster=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            command: str
            permission: str
            message: str
            async for command, permission, message in cursor:
                yield command, permission, message

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
            await self.commit()
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
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, permission,
                                           command.lower(), display, 'edit',
                                           fullMessage, user))
            await self.commit()
            return True

    async def replaceCustomCommand(self,
                                   broadcaster: str,
                                   permission: str,
                                   command: str,
                                   fullMessage: str,
                                   user: str) -> bool:
        query: str
        params: Tuple[Any, ...]
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
            if self.isSqlite:
                query = '''
REPLACE INTO custom_commands
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created, lastEditor, lastUpdated)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)
'''
                params = (broadcaster, permission, command.lower(), display,
                          fullMessage, user, user)
            else:
                query = '''
INSERT INTO custom_commands
    (broadcaster, permission, command, commandDisplay, fullMessage, creator,
    created, lastEditor, lastUpdated)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)
    ON CONFLICT ON CONSTRAINT custom_commands_pkey
    DO UPDATE SET commandDisplay=?, fullMessage=?, creator=?,
        created=CURRENT_TIMESTAMP, lastEditor=?, lastUpdated=CURRENT_TIMESTAMP
'''
                params = (broadcaster, permission, command.lower(), display,
                          fullMessage, user, user, display, fullMessage, user,
                          user)
            await cursor.execute(query, params)
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, permission,
                                           command.lower(), display, 'replace',
                                           fullMessage, user))
            await self.commit()
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
            await self.commit()
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
            await self.commit()
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
            await self.commit()
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
            await self.commit()
            return True

    async def getCustomCommandProperties(
            self, broadcaster: str
            ) -> AsyncIterator[Tuple[str, str, str, str]]:
        query: str = '''
SELECT command, permission, property, value FROM custom_command_properties
    WHERE broadcaster=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            command: str
            permission: str
            property: str
            value: str
            async for command, permission, property, value in cursor:
                yield command, permission, property, value

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
        params: Tuple[Any, ...]
        values: Dict[str, str]
        async with await self.cursor() as cursor:
            if property is None:
                query = '''
SELECT property, value FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=?
'''
                values = {}
                params = (broadcaster, permission, command.lower())
                async for p, v in await cursor.execute(query, params):
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
                async for p, v in await cursor.execute(query, params):
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
        params: Tuple[Any, ...]
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                if value is None:
                    query = '''
DELETE FROM custom_command_properties
    WHERE broadcaster=? AND permission=? AND command=? AND property=?
'''
                    params = broadcaster, permission, command.lower(), property
                else:
                    if self.isSqlite:
                        query = '''
REPLACE INTO custom_command_properties
    (broadcaster, permission, command, property, value)
    VALUES (?, ?, ?, ?, ?)
'''
                        params = (broadcaster, permission, command.lower(),
                                  property, value)
                    else:
                        query = '''
INSERT INTO custom_command_properties
    (broadcaster, permission, command, property, value)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT ON CONSTRAINT custom_command_properties_pkey
    DO UPDATE SET value=?
'''
                        params = (broadcaster, permission, command.lower(),
                                  property, value, value)
                await cursor.execute(query, params)
                await self.commit()
                return cursor.rowcount != 0
            except pyodbc.Error:
                return False

    async def getFeatures(self, broadcaster: str) -> AsyncIterator[str]:
        query: str = '''
SELECT feature FROM chat_features WHERE broadcaster=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            async for feature, in await cursor.execute(query, (broadcaster,)):
                yield feature

    async def hasFeature(self,
                         broadcaster: str,
                         feature: str) -> bool:
        if self.features is None:
            self.features = {f async for f in self.getFeatures(broadcaster)}
        return feature in self.features

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
                await self.commit()
                self.features = None
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
            self.features = None
            await self.commit()
            return cursor.rowcount != 0

    async def listBannedChannels(self) -> AsyncIterator[str]:
        query: str = '''SELECT broadcaster FROM banned_channels'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            broadcaster: str
            async for broadcaster, in await cursor.execute(query):
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
            await self.commit()
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
            await self.commit()
            return True

    async def getAllChatProperties(self, broadcaster: str
                                   ) -> AsyncIterator[Tuple[str, str]]:
        query: str = '''
SELECT property, value FROM chat_properties WHERE broadcaster=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            property: str
            value: str
            async for property, value in cursor:
                yield property, value

    @overload
    async def getChatProperty(self,
                              broadcaster: str,
                              property: str) -> Optional[str]: ...
    @overload  # noqa: F811,E301
    async def getChatProperty(self,
                              broadcaster: str,
                              property: str,
                              default: T
                              ) -> Union[str, T]: ...
    @overload  # noqa: F811,E301
    async def getChatProperty(self,
                              broadcaster: str,
                              property: str,
                              default: T,
                              parse: Callable[[str], S]
                              ) -> Union[T, S]: ...
    async def getChatProperty(self,  # type: ignore  # noqa: F811,E301
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
    @overload  # noqa: F811,E301
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: T
                                ) -> Mapping[str, Union[str, T]]: ...
    @overload  # noqa: F811,E301
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: Mapping[str, T]
                                ) -> Mapping[str, Union[str, T]]: ...
    @overload  # noqa: F811,E301
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: T,
                                parse: Mapping[str, Callable[[str], S]]
                                ) -> Mapping[str, Union[str, T, S]]: ...
    @overload  # noqa: F811,E301
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: T,
                                parse: Callable[[str], S]
                                ) -> Mapping[str, Union[T, S]]: ...
    @overload  # noqa: F811,E301
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: Mapping[str, T],
                                parse: Mapping[str, Callable[[str], S]]
                                ) -> Mapping[str, Union[str, T, S]]: ...
    @overload  # noqa: F811,E301
    async def getChatProperties(self,
                                broadcaster: str,
                                properties: Sequence[str],
                                default: Mapping[str, T],
                                parse: Callable[[str], S]
                                ) -> Mapping[str, Union[T, S]]: ...
    async def getChatProperties(self,  # type: ignore  # noqa: F811,E301
                                broadcaster,
                                properties,
                                default=None,
                                parse=None):
        query: str = '''
SELECT property, value FROM chat_properties
    WHERE broadcaster=? AND property IN (%s)
''' % ','.join('?' * len(properties))
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            values: Dict[str, Any] = {}
            params = (broadcaster,) + tuple(properties)
            async for property, value in await cursor.execute(query, params):
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
            params: Tuple[Any, ...]
            if value is None:
                query = '''
DELETE FROM chat_properties WHERE broadcaster=? AND property=?
'''
                params = broadcaster, property,
            else:
                if self.isSqlite:
                    query = '''
REPLACE INTO chat_properties (broadcaster, property, value) VALUES (?, ?, ?)
'''
                    params = broadcaster, property, value,
                else:
                    query = '''
INSERT INTO chat_properties (broadcaster, property, value) VALUES (?, ?, ?)
    ON CONFLICT ON CONSTRAINT chat_properties_pkey
    DO UPDATE SET value=?
'''
                    params = broadcaster, property, value, value,
            await cursor.execute(query, params)
            await self.commit()
            return cursor.rowcount != 0

    async def getPermittedUsers(self, broadcaster: str) -> AsyncIterator[str]:
        query: str = '''
SELECT twitchUser FROM permitted_users WHERE broadcaster=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            async for user, in await cursor.execute(query, (broadcaster,)):
                yield user

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
            await self.commit()
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
            await self.commit()
            return True

    async def getBotManagers(self) -> AsyncIterator[str]:
        query: str = '''SELECT twitchUser FROM bot_managers'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            async for manager, in await cursor.execute(query):
                yield manager

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
            await self.commit()
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
            await self.commit()
            return True

    async def getAutoRepeatToSend(self) -> AsyncIterator[AutoRepeatMessage]:
        query: str
        if self.isSqlite:
            query = '''
SELECT broadcaster, name, message FROM auto_repeat
    WHERE datetime(lastSent, '+' || duration || ' minutes')
        <= CURRENT_TIMESTAMP'''
        else:
            query = '''
SELECT broadcaster, name, message FROM auto_repeat
    WHERE lastSent + CAST((duration || ' minutes') AS INTERVAL)
        <= CURRENT_TIMESTAMP'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            row: Tuple[Any, ...]
            async for row in await cursor.execute(query):
                broadcaster, name, message = row
                yield AutoRepeatMessage(broadcaster, name, message)

    async def listAutoRepeat(self, broadcaster: str
                             ) -> AsyncIterator[AutoRepeatList]:
        query: str = '''
SELECT name, message, numLeft, duration, lastSent FROM auto_repeat
    WHERE broadcaster=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            row: Tuple[Any, ...]
            async for row in await cursor.execute(query, (broadcaster,)):
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
            await self.commit()
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
            await self.commit()
            return ret

    async def setAutoRepeat(self,
                            broadcaster: str,
                            name: str,
                            message: str,
                            count: Optional[int],
                            minutes: float) -> bool:
        cursor: aioodbc.cursor.Cursor
        query: str
        params: Tuple[Any, ...]
        async with await self.cursor() as cursor:
            if self.isSqlite:
                query = '''
REPLACE INTO auto_repeat
    (broadcaster, name, message, numLeft, duration, lastSent)
VALUES (?, ?, ?, ?, ?, datetime('now', '-' || ? || ' minutes'))
'''
                params = broadcaster, name, message, count, minutes, minutes
            else:
                query = '''
INSERT INTO auto_repeat
    (broadcaster, name, message, numLeft, duration, lastSent)
VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP - CAST((? || ' minutes') AS INTERVAL))
    ON CONFLICT ON CONSTRAINT auto_repeat_pkey
    DO UPDATE SET message=?, numLeft=?, duration=?,
    lastSent=CURRENT_TIMESTAMP - CAST((? || ' minutes') AS INTERVAL)
'''
                params = (broadcaster, name, message, count, minutes, minutes,
                          message, count, minutes, minutes)
            await cursor.execute(query, params)
            await self.commit()
            return cursor.rowcount != 0

    async def removeAutoRepeat(self,
                               broadcaster: str,
                               name: str) -> bool:
        query: str = '''
DELETE FROM auto_repeat WHERE broadcaster=? AND name=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, name))
            await self.commit()
            return cursor.rowcount != 0
