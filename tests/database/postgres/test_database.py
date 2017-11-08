import platform

import aioodbc
import asynctest

import bot  # noqa: F401

from collections.abc import Sequence

from lib.database import DatabaseMain


class TestPostgres(asynctest.TestCase):
    POOL_SIZE = 1

    async def setUp(self):
        if platform.system() == 'Windows':
            self.driver = 'PostgreSQL Unicode(x64)'
        else:
            self.driver = 'PostgreSQL UNICODE'
        self.connectionString = f'''\
Driver={self.driver};Server=localhost;Port=5432;\
Database=botgotsthis_test;Uid=botgotsthis_test;Pwd=botgotsthis_test'''
        self.pool = await aioodbc.create_pool(minsize=self.POOL_SIZE,
                                              maxsize=self.POOL_SIZE,
                                              dsn=self.connectionString)
        databaseClass = getattr(self, 'DatabaseClass', DatabaseMain)
        self.database = databaseClass(self.pool)
        await self.database.connect()
        self.cursor = await self.database.cursor()

        patcher = asynctest.patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        mock_globals = patcher.start()
        mock_globals.connectionPools = {
            'main': self.pool,
            'oauth': self.pool,
            'timeout': self.pool,
            'timezone': self.pool,
        }

    async def tearDown(self):
        await self.cursor.close()
        await self.database.close()
        self.pool.close()
        await self.pool.wait_closed()

    async def execute(self, query, params=(), *, commit=True):
        if isinstance(query, str):
            await self.cursor.execute(query, params)
        elif isinstance(query, Sequence):
            for q, p in zip(query, params if params else ((),) * len(query)):
                await self.cursor.execute(q, p)
        else:
            raise TypeError()
        if commit:
            await self.database.connection.commit()

    async def executemany(self, query, params=(), *, commit=True):
        await self.cursor.executemany(query, params)
        if commit:
            await self.database.connection.commit()

    async def value(self, query, params=()):
        await self.cursor.execute(query, params)
        return (await self.cursor.fetchone() or [None])[0]

    async def row(self, query, params=()):
        await self.cursor.execute(query, params)
        row = await self.cursor.fetchone()
        return row and tuple(row)

    async def rows(self, query, params=()):
        await self.cursor.execute(query, params)
        return [tuple(r) for r in await self.cursor.fetchall()]
