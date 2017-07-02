from tests.database.postgres.test_database import TestPostgres
from tests.database.tests.oauth import TestOAuth
from source.database import DatabaseOAuth


class TestPostgresOAuth(TestOAuth, TestPostgres):
    async def setUp(self):
        await super().setUp()
        await self.cursor.close()
        await self.database.close()
        self.database = DatabaseOAuth(self.connectionString)
        await self.database.connect()
        self.cursor = await self.database.cursor()
        await self.execute('''
CREATE TABLE oauth_tokens (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    token VARCHAR NOT NULL UNIQUE
)''')
