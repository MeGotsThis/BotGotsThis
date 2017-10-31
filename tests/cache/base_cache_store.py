import aioredis
import asynctest
from asynctest import MagicMock, patch

import bot  # noqa: F401

from lib.cache import CacheStore
from lib.database import Database, DatabaseMain


class TestCacheStore(asynctest.TestCase):
    async def setUp(self):
        self.database = MagicMock(spec=Database)
        self.database.__aenter__.side_effect = lambda: self.database
        self.database.__aexit__.return_value = False

        patcher = patch('lib.database.get_database')
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database

        self.dbmain = MagicMock(spec=DatabaseMain)
        self.dbmain.__aenter__.return_value = self.dbmain
        self.dbmain.__aexit__.return_value = False

        patcher = patch('lib.database.get_main_database')
        self.mock_dbmain = patcher.start()
        self.mock_dbmain.return_value = self.dbmain

        self.pool = await aioredis.create_pool(
            ('localhost', 6379), minsize=1, maxsize=1)
        self.data = CacheStore(self.pool)
        await self.data.open()

        self.redis = self.data.redis
        await self.redis.flushdb()

    async def tearDown(self):
        await self.data.close()
        self.pool.close()
        await self.pool.wait_closed()
