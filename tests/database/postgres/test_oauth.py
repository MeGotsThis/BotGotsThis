from tests.database.postgres.test_database import TestPostgres
from tests.database.tests.oauth import TestOAuth


class TestPostgresOAuth(TestOAuth, TestPostgres):
    async def setUp(self):
        await self.execute('''
CREATE TABLE oauth_tokens (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    token VARCHAR NOT NULL UNIQUE
)''')
