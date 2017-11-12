from asynctest import patch

import bot  # noqa: F401

from .base_cache_store import TestCacheStore
from lib.api.twitch import TwitchCommunity


class TestCacheTwitchApiNumFollowers(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        patcher = patch('lib.api.twitch.num_followers')
        self.addCleanup(patcher.stop)
        self.mock_followers = patcher.start()

    async def test(self,):
        user = 'megotsthis'
        key = f'twitch:{user}:following'
        self.mock_followers.return_value = 1
        self.assertEqual(await self.data.twitch_num_followers('megotsthis'), 1)
        self.assertTrue(self.mock_followers.called)
        self.mock_followers.reset_mock()
        self.assertEqual(await self.data.twitch_num_followers('megotsthis'), 1)
        self.assertFalse(self.mock_followers.called)
        self.assertIsNotNone(await self.redis.get(key))


class TestCacheTwitchApiId(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        patcher = patch('lib.api.twitch.getTwitchIds')
        self.addCleanup(patcher.stop)
        self.mock_ids = patcher.start()

    async def test_load_id(self):
        self.mock_ids.return_value = {'botgotsthis': '0'}
        self.assertIs(await self.data.twitch_load_id('botgotsthis'),
                      True)
        self.assertTrue(self.mock_ids.called)
        self.mock_ids.reset_mock()
        self.assertIs(await self.data.twitch_load_id('botgotsthis'),
                      True)
        self.assertFalse(self.mock_ids.called)
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchIdUserKey('botgotsthis')))
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchIdIdKey('0')))

    async def test_load_id_no_load(self):
        self.mock_ids.return_value = None
        self.assertIs(await self.data.twitch_load_id('botgotsthis'), False)
        self.assertTrue(self.mock_ids.called)
        self.mock_ids.reset_mock()
        self.assertIs(await self.data.twitch_load_id('botgotsthis'), False)
        self.assertTrue(self.mock_ids.called)
        self.assertIsNone(
            await self.redis.get(self.data._twitchIdUserKey('botgotsthis')))

    async def test_save_id(self):
        self.assertIs(await self.data.twitch_save_id('0', 'botgotsthis'),
                      True)
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchIdUserKey('botgotsthis')))
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchIdIdKey('0')))

    async def test_save_id_no_id(self):
        self.assertIs(await self.data.twitch_save_id(None, 'botgotsthis'),
                      True)
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchIdUserKey('botgotsthis')))

    async def test_is_valid_user(self):
        self.mock_ids.return_value = {'botgotsthis': '0'}
        self.assertIs(await self.data.twitch_is_valid_user('botgotsthis'),
                      True)
        self.assertTrue(self.mock_ids.called)
        self.mock_ids.reset_mock()
        self.assertIs(await self.data.twitch_is_valid_user('botgotsthis'),
                      True)
        self.assertFalse(self.mock_ids.called)

    async def test_is_valid_user_false(self):
        self.mock_ids.return_value = {}
        self.assertIs(await self.data.twitch_is_valid_user('botgotsthis'),
                      False)
        self.assertTrue(self.mock_ids.called)
        self.mock_ids.reset_mock()
        self.assertIs(await self.data.twitch_is_valid_user('botgotsthis'),
                      False)
        self.assertFalse(self.mock_ids.called)

    async def test_is_valid_user_no_load(self):
        self.mock_ids.return_value = None
        self.assertIsNone(await self.data.twitch_is_valid_user('botgotsthis'))
        self.assertTrue(self.mock_ids.called)
        self.mock_ids.reset_mock()
        self.assertIsNone(await self.data.twitch_is_valid_user('botgotsthis'))
        self.assertTrue(self.mock_ids.called)

    async def test_get_id(self):
        await self.data.twitch_save_id('0', 'botgotsthis')
        self.assertEqual(await self.data.twitch_get_id('botgotsthis'), '0')

    async def test_get_id_none(self):
        await self.data.twitch_save_id(None, 'botgotsthis')
        self.assertIsNone(await self.data.twitch_get_id('botgotsthis'))

    async def test_get_id_empty(self):
        self.assertIsNone(await self.data.twitch_get_id('botgotsthis'))

    async def test_get_user(self):
        await self.data.twitch_save_id('0', 'botgotsthis')
        self.assertEqual(await self.data.twitch_get_user('0'), 'botgotsthis')

    async def test_get_user_empty(self):
        self.assertIsNone(await self.data.twitch_get_user('0'))


class TestCacheTwitchApiCommunity(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        patcher = patch('lib.api.twitch.get_community_by_id')
        self.addCleanup(patcher.stop)
        self.mock_community_id = patcher.start()

        patcher = patch('lib.api.twitch.get_community')
        self.addCleanup(patcher.stop)
        self.mock_community_name = patcher.start()

    async def test_load_id(self):
        self.mock_community_id.return_value = TwitchCommunity(
            '0', 'botgotsthis')
        self.assertIs(await self.data.twitch_load_community_id('0'), True)
        self.assertTrue(self.mock_community_id.called)
        self.mock_community_id.reset_mock()
        self.assertIs(await self.data.twitch_load_community_id('0'), True)
        self.assertFalse(self.mock_community_id.called)
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchCommunityNameKey(
                'botgotsthis')))
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchCommunityIdKey('0')))

    async def test_load_id_no_load(self):
        self.mock_community_id.return_value = None
        self.assertIs(await self.data.twitch_load_community_id('0'),
                      False)
        self.assertTrue(self.mock_community_id.called)
        self.mock_community_id.reset_mock()
        self.assertIs(await self.data.twitch_load_community_id('0'),
                      False)
        self.assertTrue(self.mock_community_id.called)
        self.assertIsNone(
            await self.redis.get(self.data._twitchCommunityNameKey(
                'botgotsthis')))
        self.assertIsNone(
            await self.redis.get(self.data._twitchCommunityIdKey('0')))

    async def test_load_name(self):
        self.mock_community_name.return_value = TwitchCommunity(
            '0', 'botgotsthis')
        self.assertIs(
            await self.data.twitch_load_community_name('botgotsthis'), True)
        self.assertTrue(self.mock_community_name.called)
        self.mock_community_name.reset_mock()
        self.assertIs(
            await self.data.twitch_load_community_name('botgotsthis'), True)
        self.assertFalse(self.mock_community_name.called)
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchCommunityNameKey(
                'botgotsthis')))
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchCommunityIdKey('0')))

    async def test_load_name_no_load(self):
        self.mock_community_name.return_value = None
        self.assertIs(
            await self.data.twitch_load_community_name('botgotsthis'), False)
        self.assertTrue(self.mock_community_name.called)
        self.mock_community_name.reset_mock()
        self.assertIs(
            await self.data.twitch_load_community_name('botgotsthis'), False)
        self.assertTrue(self.mock_community_name.called)
        self.assertIsNone(
            await self.redis.get(self.data._twitchCommunityNameKey(
                'botgotsthis')))
        self.assertIsNone(
            await self.redis.get(self.data._twitchCommunityIdKey('0')))

    async def test_save(self):
        self.assertIs(
            await self.data.twitch_save_community('0', 'botgotsthis'), True)
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchCommunityNameKey(
                'botgotsthis')))
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchCommunityIdKey('0')))

    async def test_save_no_id(self):
        self.assertIs(
            await self.data.twitch_save_community(None, 'botgotsthis'),
            True)
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchCommunityNameKey(
                'botgotsthis')))

    async def test_save_no_name(self):
        self.assertIs(await self.data.twitch_save_community('0', None), True)
        self.assertIsNotNone(
            await self.redis.get(self.data._twitchCommunityIdKey('0')))

    async def test_get_id(self):
        await self.data.twitch_save_community('0', 'botgotsthis')
        self.assertEqual(
            await self.data.twitch_get_community_id('botgotsthis'), '0')

    async def test_get_id_none(self):
        await self.data.twitch_save_community(None, 'botgotsthis')
        self.assertIsNone(
            await self.data.twitch_get_community_id('botgotsthis'))

    async def test_get_id_empty(self):
        self.assertIsNone(
            await self.data.twitch_get_community_id('botgotsthis'))

    async def test_get_user(self):
        await self.data.twitch_save_community('0', 'botgotsthis')
        self.assertEqual(await self.data.twitch_get_community_name('0'),
                         'botgotsthis')

    async def test_get_name_none(self):
        await self.data.twitch_save_community('0', None)
        self.assertIsNone(await self.data.twitch_get_community_name('0'))

    async def test_get_user_empty(self):
        self.assertIsNone(await self.data.twitch_get_community_name('0'))
