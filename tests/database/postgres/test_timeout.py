from tests.database.postgres.test_database import TestPostgres
from tests.database.tests.test_timeout import TestTimeout
from source.database import DatabaseTimeout


class TestPostgresTimeout(TestTimeout, TestPostgres):
    async def setUp(self):
        await super().setUp()
        await self.cursor.close()
        await self.database.close()
        self.database = DatabaseTimeout(self.connectionString)
        await self.database.connect()
        self.cursor = await self.database.cursor()
        await self.execute('''
CREATE TABLE timeout_logs (
    id SERIAL NOT NULL PRIMARY KEY,
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
