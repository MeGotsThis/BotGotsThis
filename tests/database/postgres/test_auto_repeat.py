from tests.database.postgres.test_database import TestPostgres
from tests.database.tests.auto_repeat import TestAutoRepeat


class TestPostgresAutoRepeat(TestAutoRepeat, TestPostgres):
    async def setUp(self):
        await super().setUp()
        await self.execute('''
CREATE TABLE auto_repeat (
    broadcaster VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    message VARCHAR NOT NULL,
    numLeft INTEGER,
    duration REAL NOT NULL,
    lastSent TIMESTAMP NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (broadcaster, name)
);
''')
