import os

from tests.database.sqlite.test_database import TestSqlite
from lib import database
from tests.database.tests.oauth import TestOAuth


class TestSqliteOAuth(TestOAuth, TestSqlite):
    async def setUp(self):
        await super().setUp()
        sqlFile = os.path.join(
            os.path.dirname(database.__file__),
            'sqlite',
            'oauth.sql')
        with open(sqlFile) as f:
            await self.execute(f.read())
