class TestGameAbbreviation:
    async def tearDown(self):
        await self.execute(['''DROP TABLE game_abbreviations'''])
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
