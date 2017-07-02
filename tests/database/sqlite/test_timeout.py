from source.database import DatabaseTimeout
from tests.database.sqlite.test_database import TestSqlite
from tests.database.tests.test_timeout import TestTimeout


class TestSqliteTimeout(TestTimeout, TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.cursor.close()
        await self.database.close()
        self.database = DatabaseTimeout(self.connectionString)
        await self.database.connect()
        self.cursor = await self.database.cursor()
        await self.execute('''
CREATE TABLE timeout_logs (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    theTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    broadcaster VARCHAR NOT NULL,
    twitchUser VARCHAR NOT NULL,
    fromUser VARCHAR,
    module VARCHAR NOT NULL,
    level INTEGER,
    length INTEGER,
    message VARCHAR NULL,
    reason VARCHAR
)''')
