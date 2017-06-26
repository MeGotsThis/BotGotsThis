from tests.database.sqlite.test_database import TestSqlite
from source.database import DatabaseOAuth


class TestSqliteOAuth(TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.cursor.close()
        await self.database.close()
        self.database = DatabaseOAuth(self.connectionString)
        await self.database.connect()
        self.cursor = await self.database.cursor()
        await self.execute('''
CREATE TABLE oauth_tokens (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    token VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE
)''')

    async def test_get_empty(self):
        self.assertIsNone(await self.database.getOAuthToken('botgotsthis'))

    async def test_get_existing(self):
        await self.execute('INSERT INTO oauth_tokens VALUES (?, ?)',
                           ('botgotsthis', '0123456789ABCDEF'))
        self.assertEqual(await self.database.getOAuthToken('botgotsthis'),
                         '0123456789ABCDEF')

    async def test_save(self):
        await self.database.saveBroadcasterToken(
            'botgotsthis', '0123456789ABCDEF')
        self.assertEqual(await self.row('SELECT * FROM oauth_tokens'),
                         ('botgotsthis', '0123456789ABCDEF'))

    async def test_save_existing(self):
        await self.execute('INSERT INTO oauth_tokens VALUES (?, ?)',
                           ('botgotsthis', '0123456789ABCDEF'))
        await self.database.saveBroadcasterToken(
            'botgotsthis', 'FEDCBA9876543210')
        self.assertEqual(await self.row('SELECT * FROM oauth_tokens'),
                         ('botgotsthis', 'FEDCBA9876543210'))
