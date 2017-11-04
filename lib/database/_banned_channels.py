from typing import AsyncIterator, Optional, Tuple  # noqa: F401

import aioodbc.cursor  # noqa: F401
import pyodbc

from ._base import Database


class BannedChannelsMixin(Database):
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
