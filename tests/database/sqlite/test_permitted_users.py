import os

from tests.database.sqlite.test_database import TestSqlite
from lib import database
from tests.database.tests.permitted_users import TestPermittedUsers


class TestSqlitePermittedUsers(TestPermittedUsers, TestSqlite):
    async def setUp(self):
        await super().setUp()
        sqlFile = os.path.join(
            os.path.dirname(database.__file__),
            'sqlite',
            'database.sql')
        with open(sqlFile) as f:
            await self.execute(f.read())
        await self.setUpInsert()
