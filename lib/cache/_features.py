import json
from typing import Dict, Optional, Set  # noqa: F401

from ._abc import AbcCacheStore
from ..database import DatabaseMain


class FeaturesMixin(AbcCacheStore):
    def __init__(self) -> None:
        super().__init__()
        self._features: Dict[str, Set[str]] = {}

    def _featuresKey(self, broadcaster: str) -> str:
        return f'twitch:{broadcaster}:features'

    async def loadFeatures(self, broadcaster: str) -> Set[str]:
        key: str = self._featuresKey(broadcaster)
        features: Set[str]
        db: DatabaseMain
        async with DatabaseMain.acquire() as db:
            features = {feature async for feature
                        in db.getFeatures(broadcaster)}
        await self.redis.setex(key, 3600, json.dumps(list(features)))
        return features

    async def hasFeature(self, broadcaster: str, feature: str) -> bool:
        key: str = self._featuresKey(broadcaster)
        if broadcaster not in self._features:
            value: Optional[str] = await self.redis.get(key)
            features: Set[str]
            if value is None:
                features = await self.loadFeatures(broadcaster)
            else:
                features = set(json.loads(value))
            self._features[broadcaster] = features
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
        db: DatabaseMain
        async with DatabaseMain.acquire() as db:
            val = await db.addFeature(broadcaster, feature)
        if val:
            await self.resetFeatures(broadcaster)
        return val

    async def removeFeature(self,
                            broadcaster: str,
                            feature: str) -> bool:
        val: bool
        db: DatabaseMain
        async with DatabaseMain.acquire() as db:
            val = await db.removeFeature(broadcaster, feature)
        if val:
            await self.resetFeatures(broadcaster)
        return val
