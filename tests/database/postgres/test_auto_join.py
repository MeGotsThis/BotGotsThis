from tests.database.postgres.test_database import TestPostgres
from tests.database.tests.test_auto_join import TestAutoJoin


class TestPostgresAutoJoin(TestAutoJoin, TestPostgres):
    async def setUp(self):
        await super().setUp()
        await self.execute('''
CREATE TABLE auto_join (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    priority INT NOT NULL DEFAULT 0,
    cluster VARCHAR NOT NULL DEFAULT 'main'
)''')
