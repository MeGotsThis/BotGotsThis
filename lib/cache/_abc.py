from datetime import datetime

import aioredis


class AbcCacheStore:
    @property
    def redis(self) -> aioredis.Redis: ...

    async def open(self) -> None: ...

    async def close(self) -> None: ...

    @staticmethod
    def datetimeToStr(dt: datetime) -> str: ...

    @staticmethod
    def strToDatetime(dt: str) -> datetime: ...
