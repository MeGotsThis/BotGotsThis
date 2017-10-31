import aioredis


class AbcCacheStore:
    @property
    def redis(self) -> aioredis.Redis: ...

    async def open(self) -> None: ...

    async def close(self) -> None: ...
