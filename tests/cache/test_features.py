import bot  # noqa: F401

from tests.unittest.mock_class import AsyncIterator
from .base_cache_store import TestCacheStore


class TestCacheFeatures(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        self.dbmain.getFeatures.return_value = AsyncIterator(
            ['feature'])

        self.channel = 'megotsthis'
        self.key = f'twitch:{self.channel}:features'

    async def test_load(self):
        self.assertEqual(
            await self.data.loadFeatures(self.channel),
            {'feature'})
        self.assertTrue(self.dbmain.getFeatures.called)
        self.assertIsNotNone(await self.redis.get(self.key))

    async def test(self):
        self.assertTrue(
            await self.data.hasFeature(self.channel, 'feature'))
        self.assertTrue(self.dbmain.getFeatures.called)
        self.dbmain.getFeatures.reset_mock()
        self.assertFalse(
            await self.data.hasFeature(self.channel, ''))
        self.assertFalse(self.dbmain.getFeatures.called)
        self.assertIsNotNone(await self.redis.get(self.key))

    async def test_reset(self):
        await self.data.loadFeatures(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        await self.data.resetFeatures(self.channel)
        self.assertIsNone(await self.redis.get(self.key))

    async def test_add(self):
        self.dbmain.addFeature.return_value = True
        await self.data.loadFeatures(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.addFeature(self.channel, 'megotsthis'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.addFeature.called)

    async def test_add_false(self):
        self.dbmain.addFeature.return_value = False
        await self.data.loadFeatures(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.addFeature(self.channel, 'megotsthis'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.addFeature.called)

    async def test_remove(self):
        self.dbmain.removeFeature.return_value = True
        await self.data.loadFeatures(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.removeFeature(self.channel, 'megotsthis'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.removeFeature.called)

    async def test_remove_false(self):
        self.dbmain.removeFeature.return_value = False
        await self.data.loadFeatures(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.removeFeature(self.channel, 'megotsthis'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.removeFeature.called)
