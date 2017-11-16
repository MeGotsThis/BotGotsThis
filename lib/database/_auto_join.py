from typing import Any, AsyncIterator, Optional, Tuple, Union  # noqa: F401

import aioodbc.cursor  # noqa: F401
import pyodbc

from ._base import Database
from .. import data


class AutoJoinMixin(Database):
    async def getAutoJoinsChats(self) -> 'AsyncIterator[data.AutoJoinChannel]':
        query: str = '''
SELECT broadcaster, priority FROM auto_join ORDER BY priority ASC
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            r: Tuple[Any, ...]
            async for r in await cursor.execute(query):
                yield data.AutoJoinChannel(*r)

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
                           priority: Union[int, float]=0) -> bool:
        query: str = '''
INSERT INTO auto_join (broadcaster, priority) VALUES (?, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                await cursor.execute(query, (broadcaster, priority))
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
