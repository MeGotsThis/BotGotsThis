from tests.database.postgres.test_database import TestPostgres
from tests.database.tests.test_banned_channels import TestBannedChannels


class TestPostgresBannedChannels(TestBannedChannels, TestPostgres):
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
    id SERIAL NOT NULL PRIMARY KEY,
    broadcaster VARCHAR NOT NULL,
    currentTime TIMESTAMP NOT NULL,
    reason VARCHAR NOT NULL,
    who VARCHAR NOT NULL,
    actionLog VARCHAR NOT NULL
)'''])
