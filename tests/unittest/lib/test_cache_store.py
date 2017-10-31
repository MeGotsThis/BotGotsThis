import aioredis
import asynctest
from asynctest import CoroutineMock, Mock

import bot  # noqa: F401

from lib import cache


class TestCacheStore(asynctest.TestCase):
    async def setUp(self):
        self.pool = Mock(spec=aioredis.RedisPool)
        self.pool.acquire = CoroutineMock()
        self.connection = Mock(spec=aioredis.RedisConnection)
        self.connection.execute = CoroutineMock()
        self.pool.acquire.return_value = self.connection
        self.data = cache.CacheStore(self.pool)
        await self.data.open()

    async def test(self):
        await self.data.close()
