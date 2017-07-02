from tests.database.postgres.test_database import TestPostgres
from tests.database.tests.timeout import TestTimeout


class TestPostgresTimeout(TestTimeout, TestPostgres):
    async def setUp(self):
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
