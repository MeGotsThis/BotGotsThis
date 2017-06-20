import configparser
import os.path
import sqlite3

import aioodbc
import aioodbc.cursor
import aiofiles
import pyodbc

from contextlib import closing
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Iterable, Mapping, NamedTuple, Optional
from typing import Sequence, Tuple, Type, Union
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
                cursor.execute(query, (broadcaster, priority, cluster))
                self.connection.commit()
                return True
            except pyodbc.IntegrityError:
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
            except pyodbc.IntegrityError:
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
            except pyodbc.IntegrityError:
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
            except pyodbc.IntegrityError:
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
            except sqlite3.IntegrityError:
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
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            try:
                await cursor.execute(query, (broadcaster, feature))
                await self.connection.commit()
                return True
            except pyodbc.IntegrityError:
                return False

    def removeFeature(self,
                      broadcaster: str,
                      feature: str) -> bool:
        query: str = '''
DELETE FROM chat_features WHERE broadcaster=? AND feature=?'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, feature))
            self.connection.commit()
            return cursor.rowcount != 0

    def listBannedChannels(self) -> Iterable[str]:
        query: str = '''SELECT broadcaster FROM banned_channels'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            broadcaster: str
            for broadcaster, in cursor.execute(query):
                yield broadcaster

    def isChannelBannedReason(self, broadcaster: str) -> Optional[str]:
        query: str = '''
SELECT reason FROM banned_channels WHERE broadcaster=?'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster,))
            row: Optional[Tuple[str]] = cursor.fetchone()
            return row and row[0]

    def addBannedChannel(self,
                         broadcaster: str,
                         reason: str,
                         nick: str) -> bool:
        query: str = '''
INSERT INTO banned_channels 
    (broadcaster, currentTime, reason, who)
    VALUES (?, CURRENT_TIMESTAMP, ?, ?)'''
        history: str = '''
INSERT INTO banned_channels_log
    (broadcaster, currentTime, reason, who, actionLog) 
    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute(query, (broadcaster, reason, nick))
                self.connection.commit()
            except sqlite3.IntegrityError:
                return False

            cursor.execute(history, (broadcaster, reason, nick, 'add'))
            self.connection.commit()
            return True

    def removeBannedChannel(self,
                            broadcaster: str,
                            reason: str,
                            nick: str) -> bool:
        query: str = '''
DELETE FROM banned_channels WHERE broadcaster=?'''
        history: str = '''
INSERT INTO banned_channels_log
    (broadcaster, currentTime, reason, who, actionLog) 
    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster,))
            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            cursor.execute(history, (broadcaster, reason, nick, 'remove'))
            self.connection.commit()
            return True

    def getChatProperty(self,
                        broadcaster: str,
                        property: str,
                        default: Any=None,
                        parse: Optional[Callable[[str], Any]]=None) -> Any:
        query: str = '''
SELECT value FROM chat_properties WHERE broadcaster=? AND property=?'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, property,))
            row: Optional[Tuple[str]] = cursor.fetchone()
            if row is None:
                return default
            if parse is not None:
                return parse(row[0])
            return row[0]

    def getChatProperties(self,
                          broadcaster: str,
                          properties: Sequence[str],
                          default: Any=None,
                          parse: Any=None) -> Mapping[str, Any]:
        query: str = '''
SELECT property, value FROM chat_properties
    WHERE broadcaster=? AND property IN (%s)
''' % ','.join('?' * len(properties))
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            values: Dict[str, Any] = {}
            params = (broadcaster,) + tuple(properties)
            for property, value in cursor.execute(query, params):
                if isinstance(parse, dict) and property in parse:
                    value = parse[property](value)
                if isinstance(parse, Callable):  # type: ignore
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

    def setChatProperty(self,
                        broadcaster: str,
                        property: str,
                        value: Optional[str]=None) -> bool:
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            query: str
            params: tuple
            if value is None:
                query = '''
DELETE FROM chat_properties WHERE broadcaster=? AND property=?'''
                params = broadcaster, property,
            else:
                query = '''
REPLACE INTO chat_properties (broadcaster, property, value) VALUES (?, ?, ?)'''
                params = broadcaster, property, value,
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount != 0

    def isPermittedUser(self,
                        broadcaster: str,
                        user: str) -> bool:
        query: str = '''
SELECT 1 FROM permitted_users WHERE broadcaster=? AND twitchUser=?'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, user,))
            return bool(cursor.fetchone())

    def addPermittedUser(self,
                         broadcaster: str,
                         user: str,
                         moderator: str) -> bool:
        query: str = '''
INSERT INTO permitted_users (broadcaster, twitchUser) VALUES (?, ?)'''
        history: str = '''
INSERT INTO permitted_users_log
    (broadcaster, twitchUser, moderator, created, actionLog)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute(query, (broadcaster, user))
                self.connection.commit()
            except sqlite3.IntegrityError:
                return False

            cursor.execute(history, (broadcaster, user, moderator, 'add'))
            self.connection.commit()
            return True

    def removePermittedUser(self,
                            broadcaster: str,
                            user: str,
                            moderator: str) -> bool:
        query: str = '''
DELETE FROM permitted_users WHERE broadcaster=? AND twitchUser=?'''
        history: str = '''
INSERT INTO permitted_users_log
    (broadcaster, twitchUser, moderator, created, actionLog)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, user))
            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            cursor.execute(history, (broadcaster, user, moderator, 'remove'))
            self.connection.commit()
            return True

    def isBotManager(self, user: str) -> bool:
        query: str = '''SELECT 1 FROM bot_managers WHERE twitchUser=?'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (user,))
            return bool(cursor.fetchone())

    def addBotManager(self, user: str) -> bool:
        query: str = '''
INSERT INTO bot_managers (twitchUser) VALUES (?)'''
        history: str = '''
INSERT INTO bot_managers_log
    (twitchUser, created, actionLog)
    VALUES (?, CURRENT_TIMESTAMP, ?)'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute(query, (user,))
                self.connection.commit()
            except sqlite3.IntegrityError:
                return False

            cursor.execute(history, (user, 'add'))
            self.connection.commit()
            return True

    def removeBotManager(self, user: str) -> bool:
        query: str = '''
DELETE FROM bot_managers WHERE twitchUser=?'''
        history: str = '''
INSERT INTO bot_managers_log
    (twitchUser, created, actionLog)
    VALUES (?, CURRENT_TIMESTAMP, ?)'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (user,))
            self.connection.commit()
            if cursor.rowcount == 0:
                return False

            cursor.execute(history, (user, 'remove'))
            self.connection.commit()
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

    def listAutoRepeat(self, broadcaster: str) -> Iterable[AutoRepeatList]:
        query: str = '''
SELECT name, message, numLeft, duration, lastSent FROM auto_repeat
    WHERE broadcaster=?'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            row: tuple
            for row in cursor.execute(query, (broadcaster,)):
                name: str
                message: str
                count: Optional[int]
                duration: float
                last: datetime
                name, message, count, duration, last = row
                yield AutoRepeatList(name, message, count, duration, last)

    def clearAutoRepeat(self, broadcaster: str) -> bool:
        query: str = '''DELETE FROM auto_repeat WHERE broadcaster=?'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster,))
            self.connection.commit()
            return cursor.rowcount != 0

    def sentAutoRepeat(self,
                       broadcaster: str,
                       name: str) -> bool:
        query: str = '''
UPDATE auto_repeat SET numLeft=numLeft-1, lastSent=CURRENT_TIMESTAMP
    WHERE broadcaster=? AND name=?'''
        delete: str = '''
DELETE FROM auto_repeat
    WHERE broadcaster=? AND name=? AND numLeft IS NOT NULL AND numLeft<=0'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, name))
            self.connection.commit()
            ret: bool = cursor.rowcount != 0
            cursor.execute(delete, (broadcaster, name))
            self.connection.commit()
            return ret

    def setAutoRepeat(self,
                      broadcaster: str,
                      name: str,
                      message: str,
                      count: Optional[int],
                      minutes: float) -> bool:
        query: str = '''
REPLACE INTO auto_repeat (broadcaster, name, message, duration, lastSent)
VALUES (?, ?, ?, ?, datetime('now', '-' || ? || ' minutes'))'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, name, message, minutes,
                                   minutes))
            self.connection.commit()
            return cursor.rowcount != 0

    def removeAutoRepeat(self,
                         broadcaster: str,
                         name: str) -> bool:
        query: str = '''
DELETE FROM auto_repeat WHERE broadcaster=? AND name=?'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, name))
            self.connection.commit()
            return cursor.rowcount != 0


class DatabaseOAuth(Database):
    def getOAuthToken(self, broadcaster: str) -> Optional[str]:
        query: str = 'SELECT token FROM oauth.oauth_tokens WHERE broadcaster=?'
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster,))
            token: Optional[Tuple[str]] = cursor.fetchone()
            return token and token[0]

    def saveBroadcasterToken(self,
                             broadcaster: str,
                             token: str) -> None:
        query: str = '''
REPLACE INTO oauth.oauth_tokens (broadcaster, token) VALUES (?, ?)'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, (broadcaster, token))
            self.connection.commit()


class DatabaseTimeout(Database):
    def recordTimeout(self,
                      broadcaster: str,
                      user: str,
                      fromUser: Optional[str],
                      module: str,
                      level: Optional[int],
                      length: Optional[int],
                      message: Optional[str],
                      reason: Optional[str]) -> bool:
        query: str = '''
INSERT INTO timeout.timeout_logs 
    (broadcaster, twitchUser, fromUser, module, level, length, message, reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        cursor: sqlite3.Cursor
        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute(query, (broadcaster, user, fromUser, module,
                                       level, length, message, reason))
                self.connection.commit()
                return True
            except sqlite3.IntegrityError:
                return False


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
