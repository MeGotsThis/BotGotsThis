from tests.database.sqlite.test_database import TestSqlite
from tests.database.tests.oauth import TestOAuth


class TestSqliteOAuth(TestOAuth, TestSqlite):
    async def setUp(self):
        await self.execute('''
CREATE TABLE oauth_tokens (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    token VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE
)''')
