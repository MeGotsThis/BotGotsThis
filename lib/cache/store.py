from types import TracebackType  # noqa: F401
from typing import Optional, Type

import aioredis


class CacheStore:
    def __init__(self,
                 pool: aioredis.ConnectionsPool) -> None:
        self._pool: aioredis.ConnectionsPool = pool
        self._connection: Optional[aioredis.RedisConnection] = None

    @property
    def connection(self) -> aioredis.RedisConnection:
        if self._connection is None:
            raise ConnectionError('CacheStore not connected')
        return self._connection

    async def open(self) -> None:
        self._connection = await self._pool.acquire()

    async def close(self) -> None:
        if self.connection is not None:
            self._pool.release(self.connection)

    async def __aenter__(self) -> 'CacheStore':
        await self.open()
        return self

    async def __aexit__(self,
                        type: Optional[Type[BaseException]],
                        value: Optional[BaseException],
                        traceback: 'Optional[TracebackType]') -> None:
        await self.close()
