from tests.database.sqlite.test_database import TestSqlite
from tests.database.tests.test_banned_channels import TestBannedChannels


class TestSqliteBannedChannels(TestBannedChannels, TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.execute(['''
CREATE TABLE banned_channels (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    currentTime TIMESTAMP NOT NULL,
    reason VARCHAR NOT NULL,
    who VARCHAR NOT NULL
)''', '''
CREATE TABLE banned_channels_log (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    broadcaster VARCHAR NOT NULL,
    currentTime TIMESTAMP NOT NULL,
    reason VARCHAR NOT NULL,
    who VARCHAR NOT NULL,
    actionLog VARCHAR NOT NULL
)'''])
