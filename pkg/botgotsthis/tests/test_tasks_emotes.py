import asyncio
from datetime import datetime

import asynctest
from asynctest.mock import MagicMock, Mock, patch

from bot.data import Channel
from lib.cache import CacheStore
from ..tasks import emotes


class TestTasksEmotes(asynctest.TestCase):
    def setUp(self):
        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()

        self.now = datetime(2000, 1, 1)

        self.data = MagicMock(spec=CacheStore)
        self.data.__aenter__.return_value = self.data
        self.data.__aexit__.return_value = False

        patcher = patch('lib.cache.get_cache')
        self.addCleanup(patcher.stop)
        self.mock_cache = patcher.start()
        self.mock_cache.return_value = self.data

    async def test_twitch(self):
        self.data.twitch_get_bot_emote_set.return_value = {0}
        await emotes.refreshTwitchGlobalEmotes(self.now)
        self.assertTrue(self.data.twitch_get_bot_emote_set.called)
        self.assertTrue(self.data.twitch_load_emotes.called)

    async def test_twitch_no_set(self):
        self.data.twitch_get_bot_emote_set.return_value = None
        await emotes.refreshTwitchGlobalEmotes(self.now)
        self.assertTrue(self.data.twitch_get_bot_emote_set.called)
        self.assertFalse(self.data.twitch_load_emotes.called)

    async def test_twitch_multiple(self):
        async def wait(*args):
            await asyncio.sleep(0.2)
            return {0}

        async def call_0():
            return await emotes.refreshTwitchGlobalEmotes(self.now)

        async def call_1():
            await asyncio.sleep(0.1)
            return await emotes.refreshTwitchGlobalEmotes(self.now)

        self.data.twitch_get_bot_emote_set.side_effect = wait
        await asyncio.gather(call_0(), call_1())
        self.assertEqual(self.data.twitch_get_bot_emote_set.call_count, 1)
        self.assertEqual(self.data.twitch_load_emotes.call_count, 1)

    @patch(emotes.__name__ + '.refreshFfzGlobalEmotes')
    @patch(emotes.__name__ + '.refreshFfzRandomBroadcasterEmotes')
    async def test_ffz(self, mock_broadcaster, mock_global):
        await emotes.refreshFrankerFaceZEmotes(self.now)
        mock_broadcaster.assert_called_once_with(self.now)
        mock_global.assert_called_once_with(self.now)

    async def test_ffz_global(self):
        await emotes.refreshFfzGlobalEmotes(self.now)
        self.assertTrue(self.data.ffz_load_global_emotes.called)

    async def test_ffz_global_multiple(self):
        async def wait(*args, **kwargs):
            await asyncio.sleep(0.2)

        async def call_0():
            return await emotes.refreshFfzGlobalEmotes(self.now)

        async def call_1():
            await asyncio.sleep(0.1)
            return await emotes.refreshFfzGlobalEmotes(self.now)

        self.data.ffz_load_global_emotes.side_effect = wait
        await asyncio.gather(call_0(), call_1())
        self.assertEqual(self.data.ffz_load_global_emotes.call_count, 1)

    async def test_ffz_broadcaster(self):
        self.data.ffz_get_cached_broadcasters.return_value = {}
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.sessionData = {}
        self.mock_globals.channels = {'botgotsthis': channel}
        await emotes.refreshFfzRandomBroadcasterEmotes(self.now)
        self.data.ffz_load_broadcaster_emotes.assert_called_once_with(
            'botgotsthis', background=True)

    async def test_ffz_broadcaster_recent(self):
        self.data.ffz_get_cached_broadcasters.return_value = {
            'botgotsthis': 3600,
        }
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.sessionData = {}
        self.mock_globals.channels = {'botgotsthis': channel}
        await emotes.refreshFfzRandomBroadcasterEmotes(self.now)
        self.assertFalse(self.data.ffz_load_broadcaster_emotes.called)

    async def test_ffz_broadcaster_priority(self):
        self.data.ffz_get_cached_broadcasters.return_value = {}
        bgtchannel = Mock(spec=Channel)
        bgtchannel.channel = 'botgotsthis'
        bgtchannel.isStreaming = False
        bgtchannel.sessionData = {}
        mgtchannel = Mock(spec=Channel)
        mgtchannel.channel = 'megotsthis'
        mgtchannel.isStreaming = True
        mgtchannel.sessionData = {}
        self.mock_globals.channels = {'botgotsthis': bgtchannel,
                                      'megotsthis': mgtchannel}
        await emotes.refreshFfzRandomBroadcasterEmotes(self.now)
        self.data.ffz_load_broadcaster_emotes.assert_called_once_with(
            'megotsthis', background=True)

    @patch('random.choice', autospec=True)
    async def test_ffz_broadcaster_onlyone(self, mock_choice):
        self.data.ffz_get_cached_broadcasters.return_value = {}
        bgtchannel = Mock(spec=Channel)
        bgtchannel.channel = 'botgotsthis'
        bgtchannel.isStreaming = False
        bgtchannel.sessionData = {}
        mgtchannel = Mock(spec=Channel)
        mgtchannel.channel = 'megotsthis'
        mgtchannel.isStreaming = False
        mgtchannel.sessionData = {}
        self.mock_globals.channels = {'botgotsthis': bgtchannel,
                                      'megotsthis': mgtchannel}
        mock_choice.return_value = bgtchannel
        await emotes.refreshFfzRandomBroadcasterEmotes(self.now)
        self.data.ffz_load_broadcaster_emotes.assert_called_once_with(
            'botgotsthis', background=True)

    @patch('random.choice', autospec=True)
    async def test_ffz_broadcaster_empty(self, mock_choice):
        self.data.ffz_get_cached_broadcasters.return_value = {}
        self.mock_globals.channels = {}
        await emotes.refreshFfzRandomBroadcasterEmotes(self.now)
        self.assertFalse(mock_choice.called)
        self.assertFalse(self.data.ffz_load_broadcaster_emotes.called)

    @patch(emotes.__name__ + '.refreshBttvGlobalEmotes')
    @patch(emotes.__name__ + '.refreshBttvRandomBroadcasterEmotes')
    async def test_bttv(self, mock_broadcaster, mock_global):
        await emotes.refreshBetterTwitchTvEmotes(self.now)
        mock_broadcaster.assert_called_once_with(self.now)
        mock_global.assert_called_once_with(self.now)

    async def test_bttv_global(self):
        await emotes.refreshBttvGlobalEmotes(self.now)
        self.assertTrue(self.data.bttv_load_global_emotes.called)

    async def test_bttv_global_multiple(self):
        async def wait(*args, **kwargs):
            await asyncio.sleep(0.2)

        async def call_0():
            return await emotes.refreshBttvGlobalEmotes(self.now)

        async def call_1():
            await asyncio.sleep(0.1)
            return await emotes.refreshBttvGlobalEmotes(self.now)

        self.data.bttv_load_global_emotes.side_effect = wait
        await asyncio.gather(call_0(), call_1())
        self.assertEqual(self.data.bttv_load_global_emotes.call_count, 1)

    async def test_bttv_broadcaster(self):
        self.data.bttv_get_cached_broadcasters.return_value = {}
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.sessionData = {}
        self.mock_globals.channels = {'botgotsthis': channel}
        await emotes.refreshBttvRandomBroadcasterEmotes(self.now)
        self.data.bttv_load_broadcaster_emotes.assert_called_once_with(
            'botgotsthis', background=True)

    async def test_bttv_broadcaster_recent(self):
        self.data.bttv_get_cached_broadcasters.return_value = {
            'botgotsthis': 3600,
        }
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.sessionData = {}
        self.mock_globals.channels = {'botgotsthis': channel}
        await emotes.refreshBttvRandomBroadcasterEmotes(self.now)
        self.assertFalse(self.data.bttv_load_broadcaster_emotes.called)

    async def test_bttv_broadcaster_priority(self):
        self.data.bttv_get_cached_broadcasters.return_value = {}
        bgtchannel = Mock(spec=Channel)
        bgtchannel.channel = 'botgotsthis'
        bgtchannel.isStreaming = False
        bgtchannel.sessionData = {}
        mgtchannel = Mock(spec=Channel)
        mgtchannel.channel = 'megotsthis'
        mgtchannel.isStreaming = True
        mgtchannel.sessionData = {}
        self.mock_globals.channels = {'botgotsthis': bgtchannel,
                                      'megotsthis': mgtchannel}
        await emotes.refreshBttvRandomBroadcasterEmotes(self.now)
        self.data.bttv_load_broadcaster_emotes.assert_called_once_with(
            'megotsthis', background=True)

    @patch('random.choice', autospec=True)
    async def test_bttv_broadcaster_onlyone(self, mock_choice):
        self.data.bttv_get_cached_broadcasters.return_value = {}
        bgtchannel = Mock(spec=Channel)
        bgtchannel.channel = 'botgotsthis'
        bgtchannel.isStreaming = False
        bgtchannel.sessionData = {}
        mgtchannel = Mock(spec=Channel)
        mgtchannel.channel = 'megotsthis'
        mgtchannel.isStreaming = False
        mgtchannel.sessionData = {}
        self.mock_globals.channels = {'botgotsthis': bgtchannel,
                                      'megotsthis': mgtchannel}
        mock_choice.return_value = bgtchannel
        await emotes.refreshBttvRandomBroadcasterEmotes(self.now)
        self.data.bttv_load_broadcaster_emotes.assert_called_once_with(
            'botgotsthis', background=True)

    @patch('random.choice', autospec=True)
    async def test_bttv_broadcaster_empty(self, mock_choice):
        self.data.bttv_get_cached_broadcasters.return_value = {}
        self.mock_globals.channels = {}
        await emotes.refreshBttvRandomBroadcasterEmotes(self.now)
        self.assertFalse(mock_choice.called)
        self.assertFalse(self.data.bttv_load_broadcaster_emotes.called)
