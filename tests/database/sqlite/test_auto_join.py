from tests.database.sqlite.test_database import TestSqlite
from tests.database.tests.auto_join import TestAutoJoin


class TestSqliteAutoJoin(TestAutoJoin, TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.execute('''
CREATE TABLE auto_join (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    priority INT NOT NULL DEFAULT 0,
    cluster VARCHAR NOT NULL DEFAULT 'main'
)''')
