import bot  # noqa: F401

from tests.unittest.mock_class import AsyncIterator
from .base_cache_store import TestCacheStore


class TestCacheBotMangers(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        self.dbmain.getGameAbbreviations.return_value = AsyncIterator([
            ('kappa', 'FrankerZ'),
        ])

    async def test_load(self):
        self.assertEqual(
            await self.data.loadGameAbbreviations(),
            {'kappa': 'FrankerZ'})
        self.assertTrue(self.dbmain.getGameAbbreviations.called)
        self.assertIsNotNone(await self.redis.get('game-abbreviation'))

    async def test(self):
        self.assertEqual(await self.data.getFullGameTitle('kappa'),
                         'FrankerZ')
        self.assertTrue(self.dbmain.getGameAbbreviations.called)
        self.dbmain.getGameAbbreviations.reset_mock()
        self.assertIsNone(await self.data.getFullGameTitle(''))
        self.assertFalse(self.dbmain.getGameAbbreviations.called)
        self.assertIsNotNone(await self.redis.get('game-abbreviation'))

    async def test_not_existing(self):
        self.assertIsNone(await self.data.getFullGameTitle('kappahd'))

    async def test_abbreviation(self):
        self.assertEqual(await self.data.getFullGameTitle('kappa'), 'FrankerZ')

    async def test_casing(self):
        self.assertEqual(await self.data.getFullGameTitle('Kappa'), 'FrankerZ')

    async def test_twitch_game(self):
        self.assertEqual(await self.data.getFullGameTitle('FrankerZ'),
                         'FrankerZ')

    async def test_twitch_game_casing(self):
        self.assertEqual(await self.data.getFullGameTitle('frankerz'),
                         'FrankerZ')

    async def test_reset(self):
        await self.data.loadGameAbbreviations()
        self.assertIsNotNone(await self.redis.get('game-abbreviation'))
        await self.data.resetGameAbbreviations()
        self.assertIsNone(await self.redis.get('game-abbreviation'))
