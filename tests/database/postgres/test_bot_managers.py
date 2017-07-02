from tests.database.postgres.test_database import TestPostgres
from tests.database.tests.test_bot_managers import TestBotManagers


class TestPostgresBotMangers(TestBotManagers, TestPostgres):
    async def setUp(self):
        await super().setUp()
        await self.execute(['''
CREATE TABLE bot_managers (
    twitchUser VARCHAR NOT NULL PRIMARY KEY
)''', '''
CREATE TABLE bot_managers_log (
    id SERIAL NOT NULL PRIMARY KEY,
    twitchUser VARCHAR NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actionLog VARCHAR NOT NULL
)''', '''
INSERT INTO bot_managers VALUES ('megotsthis')'''])
