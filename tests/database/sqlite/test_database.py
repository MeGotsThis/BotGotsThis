import platform

import asynctest

import bot  # noqa: F401

from collections.abc import Sequence

from source.database import DatabaseMain


class TestSqlite(asynctest.TestCase):
    async def setUp(self):
        if platform.system() == 'Windows':
            self.connectionString = '''\
Driver=SQLite3 ODBC Driver;Database=:memory:;FKSupport=true;'''
        else:
            self.connectionString = '''\
Driver=SQLite3;Database=:memory:;FKSupport=true;'''
        databaseClass = getattr(self, 'DatabaseClass', DatabaseMain)
        self.database = databaseClass(self.connectionString)
        await self.database.connect()
        self.cursor = await self.database.cursor()

    async def tearDown(self):
        await self.cursor.close()
        await self.database.close()

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
