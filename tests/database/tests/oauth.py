from source.database import DatabaseOAuth


class TestOAuth:
    DatabaseClass = DatabaseOAuth

    async def tearDown(self):
        await self.execute('''DROP TABLE oauth_tokens''')
        await super().tearDown()

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
