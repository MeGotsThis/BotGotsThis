import json
from typing import Dict, List, Optional, Set  # noqa: F401

from ._abc import AbcCacheStore
from .. import database


class FeaturesMixin(AbcCacheStore):
    def __init__(self):
        self._features: Dict[str, Set[str]] = {}

    def _featuresKey(self, broadcaster: str) -> str:
        return f'twitch:{broadcaster}:features'

    async def hasFeature(self, broadcaster: str, feature: str) -> bool:
        key: str = self._featuresKey(broadcaster)
        value: Optional[str] = await self.redis.get(key)
        if broadcaster not in self._features:
            if value is None:
                db: database.DatabaseMain
                async with database.get_main_database() as db:
                    self._features[broadcaster] = {
                        feature async for feature
                        in db.getFeatures(broadcaster)}
                data: List[str] = list(self._features[broadcaster])
                await self.redis.setex(key, 3600, json.dumps(data))
            else:
                self._features = set(json.loads(value))
        return feature in self._features[broadcaster]

    async def resetFeatures(self, broadcaster: str) -> None:
        key: str = self._featuresKey(broadcaster)
        await self.redis.delete(key)
        if broadcaster in self._features:
            del self._features[broadcaster]

    async def addFeature(self,
                         broadcaster: str,
                         feature: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.addFeature(broadcaster, feature)
        if val:
            await self.resetFeatures(broadcaster)
        return val

    async def removeFeature(self,
                            broadcaster: str,
                            feature: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.removeFeature(broadcaster, feature)
        if val:
            await self.resetFeatures(broadcaster)
        return val
