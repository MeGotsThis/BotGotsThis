from asynctest import patch

import bot  # noqa: F401

from .base_cache_store import TestCacheStore


class TestCacheBttvApiGlobalEmotes(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        patcher = patch('lib.api.bttv.getGlobalEmotes')
        self.addCleanup(patcher.stop)
        self.mock_emotes = patcher.start()
        self.mock_emotes.return_value = {
            '54fa925e01e468494b85b54d': 'OhMyGoodness'
        }

    async def test_load(self):
        self.assertIs(await self.data.bttv_load_global_emotes(), True)
        self.assertTrue(self.mock_emotes.called)
        self.mock_emotes.reset_mock()
        self.assertIs(await self.data.bttv_load_global_emotes(), True)
        self.assertFalse(self.mock_emotes.called)
        self.assertIsNotNone(
            await self.redis.get(self.data._bttvGlobalEmoteKey()))

    async def test_load_background(self):
        self.assertIs(await self.data.bttv_load_global_emotes(background=True),
                      True)
        self.assertTrue(self.mock_emotes.called)
        self.data.redis.expire(self.data._bttvGlobalEmoteKey(), 5)
        self.mock_emotes.reset_mock()
        self.assertIs(await self.data.bttv_load_global_emotes(background=True),
                      True)
        self.assertTrue(self.mock_emotes.called)
        self.assertIsNotNone(
            await self.redis.get(self.data._bttvGlobalEmoteKey()))

    async def test_load_none(self):
        self.mock_emotes.return_value = None
        self.assertIs(await self.data.bttv_load_global_emotes(), False)
        self.assertTrue(self.mock_emotes.called)
        self.mock_emotes.reset_mock()
        self.assertIs(await self.data.bttv_load_global_emotes(), False)
        self.assertTrue(self.mock_emotes.called)
        self.assertIsNone(
            await self.redis.get(self.data._bttvGlobalEmoteKey()))

    async def test_save(self):
        self.assertIs(
            await self.data.bttv_save_global_emotes(
                {'54fa925e01e468494b85b54d': 'OhMyGoodness'}),
            True)
        self.assertIsNotNone(
            await self.redis.get(self.data._bttvGlobalEmoteKey()))

    async def test_get(self):
        await self.data.bttv_save_global_emotes(
            {'54fa925e01e468494b85b54d': 'OhMyGoodness'})
        self.assertEqual(await self.data.bttv_get_global_emotes(),
                         {'54fa925e01e468494b85b54d': 'OhMyGoodness'})

    async def test_get_empty(self):
        self.assertIsNone(await self.data.bttv_get_global_emotes())


class TestCacheBttvApiBroadcasterEmotes(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        patcher = patch('lib.api.bttv.getBroadcasterEmotes')
        self.addCleanup(patcher.stop)
        self.mock_emotes = patcher.start()
        self.mock_emotes.return_value = {'554da1a289d53f2d12781907': '(ditto)'}

    async def test_load(self):
        self.assertIs(
            await self.data.bttv_load_broadcaster_emotes('botgotsthis'), True)
        self.assertTrue(self.mock_emotes.called)
        self.mock_emotes.reset_mock()
        self.assertIs(
            await self.data.bttv_load_broadcaster_emotes('botgotsthis'), True)
        self.assertFalse(self.mock_emotes.called)
        self.assertIsNotNone(
            await self.redis.get(
                self.data._bttvBroadcasterEmoteKey('botgotsthis')))

    async def test_load_background(self):
        self.assertIs(
            await self.data.bttv_load_broadcaster_emotes(
                'botgotsthis', background=True),
            True)
        self.assertTrue(self.mock_emotes.called)
        self.data.redis.expire(
            self.data._bttvBroadcasterEmoteKey('botgotsthis'), 5)
        self.mock_emotes.reset_mock()
        self.assertIs(
            await self.data.bttv_load_broadcaster_emotes(
                'botgotsthis', background=True),
            True)
        self.assertTrue(self.mock_emotes.called)
        self.assertIsNotNone(
            await self.redis.get(
                self.data._bttvBroadcasterEmoteKey('botgotsthis')))

    async def test_load_none(self):
        self.mock_emotes.return_value = None
        self.assertIs(
            await self.data.bttv_load_broadcaster_emotes('botgotsthis'), False)
        self.assertTrue(self.mock_emotes.called)
        self.mock_emotes.reset_mock()
        self.assertIs(
            await self.data.bttv_load_broadcaster_emotes('botgotsthis'), False)
        self.assertTrue(self.mock_emotes.called)
        self.assertIsNone(
            await self.redis.get(
                self.data._bttvBroadcasterEmoteKey('botgotsthis')))

    async def test_save(self):
        self.assertIs(
            await self.data.bttv_save_broadcaster_emotes(
                'botgotsthis', {'554da1a289d53f2d12781907': '(ditto)'}),
            True)
        self.assertIsNotNone(
            await self.redis.get(
                self.data._bttvBroadcasterEmoteKey('botgotsthis')))

    async def test_get(self):
        await self.data.bttv_save_broadcaster_emotes(
            'botgotsthis', {'554da1a289d53f2d12781907': '(ditto)'})
        self.assertEqual(
            await self.data.bttv_get_broadcaster_emotes('botgotsthis'),
            {'554da1a289d53f2d12781907': '(ditto)'})

    async def test_get_empty(self):
        self.assertIsNone(
            await self.data.bttv_get_broadcaster_emotes('botgotsthis'))
