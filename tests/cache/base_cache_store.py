import aioredis
import asynctest
from asynctest import MagicMock, patch

import bot  # noqa: F401
import tests.unittest.asynctest_fix  # noqa: F401

from lib.cache import CacheStore
from lib.database import DatabaseMain


class TestCacheStore(asynctest.TestCase):
    async def setUp(self):
        self.dbmain = MagicMock(spec=DatabaseMain)
        self.dbmain.__aenter__.return_value = self.dbmain
        self.dbmain.__aexit__.return_value = False

        patcher = patch.object(DatabaseMain, 'acquire')
        self.addCleanup(patcher.stop)
        self.mock_dbmain = patcher.start()
        self.mock_dbmain.return_value = self.dbmain

        self.pool = await aioredis.create_pool(
            ('localhost', 6379),
            encoding='utf-8',
            minsize=1, maxsize=1)
        self.data = CacheStore(self.pool)
        await self.data.open()

        self.redis = self.data.redis
        await self.redis.flushdb()

    async def tearDown(self):
        await self.data.close()
        self.pool.close()
        await self.pool.wait_closed()
