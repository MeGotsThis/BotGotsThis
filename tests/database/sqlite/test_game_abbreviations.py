from tests.database.sqlite.test_database import TestSqlite


class TestSqliteGameAbbreviation(TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.execute(['''
CREATE TABLE game_abbreviations (
    abbreviation VARCHAR NOT NULL COLLATE NOCASE PRIMARY KEY,
    twitchGame VARCHAR NOT NULL COLLATE NOCASE
)''', '''
CREATE INDEX game_abbreviations_game ON game_abbreviations (twitchGame)'''])
        await self.execute('INSERT INTO game_abbreviations VALUES (?, ?)',
                           ('kappa', 'FrankerZ'))

    async def tearDown(self):
        await self.execute('DROP TABLE IF EXISTS game_abbreviations')
        await super().tearDown()

    async def test_not_existing(self):
        self.assertIsNone(await self.database.getFullGameTitle('kappahd'))

    async def test_abbreviation(self):
        self.assertEqual(await self.database.getFullGameTitle('kappa'),
                         'FrankerZ')

    async def test_casing(self):
        self.assertEqual(await self.database.getFullGameTitle('Kappa'),
                         'FrankerZ')

    async def test_twitch_game(self):
        self.assertEqual(await self.database.getFullGameTitle('FrankerZ'),
                         'FrankerZ')

    async def test_twitch_game_casing(self):
        self.assertEqual(await self.database.getFullGameTitle('frankerz'),
                         'FrankerZ')
