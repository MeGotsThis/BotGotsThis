from tests.database.sqlite.test_database import TestSqlite
from tests.database.tests.test_bot_managers import TestBotManagers


class TestSqliteBotManagers(TestBotManagers, TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.execute(['''
CREATE TABLE bot_managers (
    twitchUser VARCHAR NOT NULL PRIMARY KEY
)''', '''
CREATE TABLE bot_managers_log (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    twitchUser VARCHAR NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actionLog VARCHAR NOT NULL
)''', '''
INSERT INTO bot_managers VALUES ('megotsthis')'''])
