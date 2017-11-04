import aioodbc.cursor  # noqa: F401
import pyodbc

from datetime import datetime  # noqa: F401
from typing import Any, AsyncIterator, Callable, Dict, Mapping  # noqa: F401,E501
from typing import Optional, Sequence, Set, Tuple, TypeVar, Union  # noqa: F401
from typing import overload

from ._auto_join import AutoJoinMixin
from ._base import Database
from ._custom_commands import CustomCommandsMixin
from ._features import FeaturesMixin
from ._game_abbreviations import GameAbbreviationsMixin
from .. import data

T = TypeVar('T')
S = TypeVar('S')


class DatabaseMain(AutoJoinMixin, GameAbbreviationsMixin, CustomCommandsMixin,
                   FeaturesMixin, Database):
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

    async def getAutoRepeats(self) -> 'AsyncIterator[data.RepeatData]':
        query: str = '''
SELECT broadcaster, name, message, numLeft, duration, lastSent
    FROM auto_repeat
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            row: Tuple[str, str, str, Optional[int], float, datetime]
            broadcaster: str
            name: str
            message: str
            count: Optional[int]
            duration: float
            last: datetime
            async for (broadcaster, name, message, count, duration,
                       last) in await cursor.execute(query):
                yield data.RepeatData(broadcaster, name, message, count,
                                      duration, last)

    async def getAutoRepeatToSend(self
                                  ) -> 'AsyncIterator[data.AutoRepeatMessage]':
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
                yield data.AutoRepeatMessage(broadcaster, name, message)

    async def listAutoRepeat(self, broadcaster: str
                             ) -> 'AsyncIterator[data.AutoRepeatList]':
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
                yield data.AutoRepeatList(name, message, count, duration, last)

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
