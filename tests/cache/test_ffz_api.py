from asynctest import patch

import bot  # noqa: F401

from .base_cache_store import TestCacheStore


class TestCacheFfzApiGlobalEmotes(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        patcher = patch('lib.api.ffz.getGlobalEmotes')
        self.addCleanup(patcher.stop)
        self.mock_emotes = patcher.start()
        self.mock_emotes.return_value = {3: 'BeanieHipster'}

    async def test_load(self):
        self.assertIs(await self.data.ffz_load_global_emotes(), True)
        self.assertTrue(self.mock_emotes.called)
        self.mock_emotes.reset_mock()
        self.assertIs(await self.data.ffz_load_global_emotes(), True)
        self.assertFalse(self.mock_emotes.called)
        self.assertIsNotNone(
            await self.redis.get(self.data._ffzGlobalEmoteKey()))

    async def test_load_background(self):
        self.assertIs(await self.data.ffz_load_global_emotes(background=True),
                      True)
        self.assertTrue(self.mock_emotes.called)
        self.data.redis.expire(self.data._ffzGlobalEmoteKey(), 5)
        self.mock_emotes.reset_mock()
        self.assertIs(await self.data.ffz_load_global_emotes(background=True),
                      True)
        self.assertTrue(self.mock_emotes.called)
        self.assertIsNotNone(
            await self.redis.get(self.data._ffzGlobalEmoteKey()))

    async def test_load_none(self):
        self.mock_emotes.return_value = None
        self.assertIs(await self.data.ffz_load_global_emotes(), False)
        self.assertTrue(self.mock_emotes.called)
        self.mock_emotes.reset_mock()
        self.assertIs(await self.data.ffz_load_global_emotes(), False)
        self.assertTrue(self.mock_emotes.called)
        self.assertIsNone(await self.redis.get(self.data._ffzGlobalEmoteKey()))

    async def test_save(self):
        self.assertIs(
            await self.data.ffz_save_global_emotes({3: 'BeanieHipster'}), True)
        self.assertIsNotNone(
            await self.redis.get(self.data._ffzGlobalEmoteKey()))

    async def test_get(self):
        await self.data.ffz_save_global_emotes({3: 'BeanieHipster'})
        self.assertEqual(await self.data.ffz_get_global_emotes(),
                         {3: 'BeanieHipster'})

    async def test_get_empty(self):
        self.assertIsNone(await self.data.ffz_get_global_emotes())


class TestCacheFfzApiBroadcasterEmotes(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        patcher = patch('lib.api.ffz.getBroadcasterEmotes')
        self.addCleanup(patcher.stop)
        self.mock_emotes = patcher.start()
        self.mock_emotes.return_value = {18146: 'KevinSquirtle'}

    async def test_load(self):
        self.assertIs(
            await self.data.ffz_load_broadcaster_emotes('botgotsthis'), True)
        self.assertTrue(self.mock_emotes.called)
        self.mock_emotes.reset_mock()
        self.assertIs(
            await self.data.ffz_load_broadcaster_emotes('botgotsthis'), True)
        self.assertFalse(self.mock_emotes.called)
        self.assertIsNotNone(
            await self.redis.get(
                self.data._ffzBroadcasterEmoteKey('botgotsthis')))

    async def test_load_background(self):
        self.assertIs(
            await self.data.ffz_load_broadcaster_emotes(
                'botgotsthis', background=True),
            True)
        self.assertTrue(self.mock_emotes.called)
        self.data.redis.expire(
            self.data._ffzBroadcasterEmoteKey('botgotsthis'), 5)
        self.mock_emotes.reset_mock()
        self.assertIs(
            await self.data.ffz_load_broadcaster_emotes(
                'botgotsthis', background=True),
            True)
        self.assertTrue(self.mock_emotes.called)
        self.assertIsNotNone(
            await self.redis.get(
                self.data._ffzBroadcasterEmoteKey('botgotsthis')))

    async def test_load_none(self):
        self.mock_emotes.return_value = None
        self.assertIs(
            await self.data.ffz_load_broadcaster_emotes('botgotsthis'), False)
        self.assertTrue(self.mock_emotes.called)
        self.mock_emotes.reset_mock()
        self.assertIs(
            await self.data.ffz_load_broadcaster_emotes('botgotsthis'), False)
        self.assertTrue(self.mock_emotes.called)
        self.assertIsNone(
            await self.redis.get(
                self.data._ffzBroadcasterEmoteKey('botgotsthis')))

    async def test_save(self):
        self.assertIs(
            await self.data.ffz_save_broadcaster_emotes(
                'botgotsthis', {18146: 'KevinSquirtle'}),
            True)
        self.assertIsNotNone(
            await self.redis.get(
                self.data._ffzBroadcasterEmoteKey('botgotsthis')))

    async def test_get(self):
        await self.data.ffz_save_broadcaster_emotes(
            'botgotsthis', {18146: 'KevinSquirtle'})
        self.assertEqual(
            await self.data.ffz_get_broadcaster_emotes('botgotsthis'),
            {18146: 'KevinSquirtle'})

    async def test_get_empty(self):
        self.assertIsNone(
            await self.data.ffz_get_broadcaster_emotes('botgotsthis'))
