from ._drop_tables import TestDropTables


class TestGameAbbreviation(TestDropTables):
    async def setUpInsert(self):
        await self.execute('INSERT INTO game_abbreviations VALUES (?, ?)',
                           ('kappa', 'FrankerZ'))

    async def test_get_all(self):
        self.assertEqual(
            [r async for r in self.database.getGameAbbreviations()],
            [('kappa', 'FrankerZ')])

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
