from asynctest import patch

import bot  # noqa: F401

from .base_cache_store import TestCacheStore


class TestCachePermittedUsers(TestCacheStore):
    async def setUp(self):
        await super().setUp()

    @patch('lib.api.twitch.num_followers')
    async def test(self, mock_followers):
        user = 'megotsthis'
        key = f'twitch:{user}:following'
        mock_followers.return_value = 1
        self.assertEqual(await self.data.twitch_num_followers('megotsthis'), 1)
        self.assertTrue(mock_followers.called)
        mock_followers.reset_mock()
        self.assertEqual(await self.data.twitch_num_followers('megotsthis'), 1)
        self.assertFalse(mock_followers.called)
        self.assertIsNotNone(await self.redis.get(key))
