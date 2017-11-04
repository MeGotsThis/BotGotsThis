from typing import AsyncIterator, Optional, Set  # noqa: F401

import aioodbc.cursor  # noqa: F401
import pyodbc

from ._base import Database


class FeaturesMixin(Database):
    def __init__(self,
                 pool: aioodbc.Pool) -> None:
        super().__init__(pool)
        self._features: Optional[Set[str]] = None

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
        if self._features is None:
            self._features = {f async for f in self.getFeatures(broadcaster)}
        return feature in self._features

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
