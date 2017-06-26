from datetime import datetime
from tests.database.sqlite.test_database import TestSqlite
from tests.unittest.mock_class import TypeMatch
from source.database import DatabaseTimeout


class TestSqliteTimeout(TestSqlite):
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

    async def tearDown(self):
        await self.execute('DROP TABLE IF EXISTS timeout_logs')
        await super().setUp()

    async def test_record(self):
        await self.database.recordTimeout(
            'botgotsthis', 'botgotsthis', None, 'tests', None, None, None,
            None)
        self.assertEqual(
            await self.row('SELECT * FROM timeout_logs'),
            (1, TypeMatch(datetime), 'botgotsthis', 'botgotsthis', None,
             'tests', None, None, None, None))

    async def test_record2(self):
        await self.database.recordTimeout(
            'botgotsthis', 'megotsthis', 'mebotsthis', 'tests', 0, 3600,
            'Kappa', 'KappaHD')
        self.assertEqual(
            await self.row('SELECT * FROM timeout_logs'),
            (1, TypeMatch(datetime), 'botgotsthis', 'megotsthis', 'mebotsthis',
             'tests', 0, 3600, 'Kappa', 'KappaHD'))
