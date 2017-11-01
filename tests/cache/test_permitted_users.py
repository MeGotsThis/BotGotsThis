import bot  # noqa: F401

from tests.unittest.mock_class import AsyncIterator
from .base_cache_store import TestCacheStore


class TestCacheBotMangers(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        self.dbmain.getPermittedUsers.return_value = AsyncIterator(
            ['botgotsthis'])

        self.channel = 'megotsthis'
        self.key = f'twitch:{self.channel}:permitted'

    async def test(self):
        self.assertTrue(
            await self.data.isPermittedUser(self.channel, 'botgotsthis'))
        self.assertTrue(self.dbmain.getPermittedUsers.called)
        self.dbmain.getPermittedUsers.reset_mock()
        self.assertFalse(
            await self.data.isPermittedUser(self.channel, 'megotsthis'))
        self.assertFalse(self.dbmain.getPermittedUsers.called)
        self.assertIsNotNone(await self.redis.get(self.key))

    async def test_reset(self):
        await self.data.isPermittedUser(self.channel, 'botgotsthis')
        self.assertIsNotNone(await self.redis.get(self.key))
        await self.data.resetPermittedUsers(self.channel)
        self.assertIsNone(await self.redis.get(self.key))

    async def test_add(self):
        self.dbmain.addPermittedUser.return_value = True
        await self.data.isPermittedUser(self.channel, 'botgotsthis')
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.addPermittedUser(self.channel, 'megotsthis',
                                             'mebotsthis'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.addPermittedUser.called)

    async def test_add_false(self):
        self.dbmain.addPermittedUser.return_value = False
        await self.data.isPermittedUser(self.channel, 'botgotsthis')
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.addPermittedUser(self.channel, 'megotsthis',
                                             'mebotsthis'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.addPermittedUser.called)

    async def test_remove(self):
        self.dbmain.removePermittedUser.return_value = True
        await self.data.isPermittedUser(self.channel, 'botgotsthis')
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.removePermittedUser(self.channel, 'megotsthis',
                                                'mebotsthis'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.removePermittedUser.called)

    async def test_remove_false(self):
        self.dbmain.removePermittedUser.return_value = False
        await self.data.isPermittedUser(self.channel, 'botgotsthis')
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.removePermittedUser(self.channel, 'megotsthis',
                                                'mebotsthis'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.removePermittedUser.called)
