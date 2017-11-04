import aioodbc.cursor  # noqa: F401

from datetime import datetime  # noqa: F401
from typing import Any, AsyncIterator  # noqa: F401
from typing import Optional, Tuple  # noqa: F401

from ._auto_join import AutoJoinMixin
from ._banned_channels import BannedChannelsMixin
from ._bot_managers import BotManagersMixin
from ._base import Database
from ._chat_properties import ChatPropertiesMixin
from ._custom_commands import CustomCommandsMixin
from ._features import FeaturesMixin
from ._game_abbreviations import GameAbbreviationsMixin
from ._permitted_users import PermittedUsersMixin
from .. import data


class DatabaseMain(AutoJoinMixin, GameAbbreviationsMixin, CustomCommandsMixin,
                   FeaturesMixin, BannedChannelsMixin, ChatPropertiesMixin,
                   PermittedUsersMixin, BotManagersMixin, Database):
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
