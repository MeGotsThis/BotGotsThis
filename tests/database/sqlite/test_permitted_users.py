from tests.database.sqlite.test_database import TestSqlite
from tests.database.tests.permitted_users import TestPermittedUsers


class TestSqlitePermittedUsers(TestPermittedUsers, TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.execute(['''
CREATE TABLE permitted_users (
    broadcaster VARCHAR NOT NULL,
    twitchUser VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, twitchUser)
)''', '''
CREATE TABLE permitted_users_log (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    broadcaster VARCHAR NOT NULL,
    twitchUser VARCHAR NOT NULL,
    moderator VARCHAR NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actionLog VARCHAR NOT NULL
)''', '''
INSERT INTO permitted_users VALUES ('botgotsthis', 'megotsthis')'''])
