import aioredis
import asynctest
from datetime import datetime
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

    async def test_datetime_str(self):
        dt = datetime(2000, 1, 1)
        self.assertEqual(dt,
                         self.data.strToDatetime(self.data.datetimeToStr(dt)))

    async def test_datetime_str_microsecond(self):
        dt = datetime(2000, 1, 1, 0, 0, 0, 1)
        self.assertEqual(dt,
                         self.data.strToDatetime(self.data.datetimeToStr(dt)))

    async def test_datetime_str_none(self):
        self.assertIsNone(self.data.strToDatetime(None))
