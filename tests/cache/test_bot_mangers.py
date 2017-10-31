import bot  # noqa: F401

from tests.unittest.mock_class import AsyncIterator
from .base_cache_store import TestCacheStore


class TestCacheBotMangers(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        self.dbmain.getBotManagers.return_value = AsyncIterator(
            ['botgotsthis'])

    async def test(self):
        self.assertTrue(await self.data.isBotManager('botgotsthis'))
        self.assertTrue(self.dbmain.getBotManagers.called)
        self.dbmain.getBotManagers.reset_mock()
        self.assertFalse(await self.data.isBotManager('megotsthis'))
        self.assertFalse(self.dbmain.getBotManagers.called)
        self.assertIsNotNone(await self.redis.get('managers'))

    async def test_reset(self):
        await self.data.isBotManager('botgotsthis')
        self.assertIsNotNone(await self.redis.get('managers'))
        await self.data.resetBotManagers()
        self.assertIsNone(await self.redis.get('managers'))

    async def test_add(self):
        self.dbmain.addBotManager.return_value = True
        await self.data.isBotManager('botgotsthis')
        self.assertIsNotNone(await self.redis.get('managers'))
        self.assertIs(await self.data.addBotManager('megotsthis'), True)
        self.assertIsNone(await self.redis.get('managers'))
        self.assertTrue(self.dbmain.addBotManager.called)

    async def test_add_false(self):
        self.dbmain.addBotManager.return_value = False
        await self.data.isBotManager('botgotsthis')
        self.assertIsNotNone(await self.redis.get('managers'))
        self.assertIs(await self.data.addBotManager('megotsthis'), False)
        self.assertIsNotNone(await self.redis.get('managers'))
        self.assertTrue(self.dbmain.addBotManager.called)

    async def test_remove(self):
        self.dbmain.removeBotManager.return_value = True
        await self.data.isBotManager('botgotsthis')
        self.assertIsNotNone(await self.redis.get('managers'))
        self.assertIs(await self.data.removeBotManager('megotsthis'), True)
        self.assertIsNone(await self.redis.get('managers'))
        self.assertTrue(self.dbmain.removeBotManager.called)

    async def test_remove_false(self):
        self.dbmain.removeBotManager.return_value = False
        await self.data.isBotManager('botgotsthis')
        self.assertIsNotNone(await self.redis.get('managers'))
        self.assertIs(await self.data.removeBotManager('megotsthis'), False)
        self.assertIsNotNone(await self.redis.get('managers'))
        self.assertTrue(self.dbmain.removeBotManager.called)
