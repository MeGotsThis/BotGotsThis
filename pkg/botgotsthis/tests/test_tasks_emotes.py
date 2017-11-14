import asyncio
from datetime import datetime, timedelta

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

    @patch('lib.api.ffz.getGlobalEmotes')
    async def test_ffz_global(self, mock_emotes):
        self.mock_globals.globalFfzEmotesCache = self.now
        self.mock_globals.globalFfzEmotes = {}
        emotes_ = {1: 'ZreknarF'}
        mock_emotes.return_value = emotes_
        await emotes.refreshFfzGlobalEmotes(self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalFfzEmotesCache,
                         self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalFfzEmotes, emotes_)
        mock_emotes.assert_called_once_with()

    @patch('lib.api.ffz.getGlobalEmotes')
    async def test_ffz_global_recent(self, mock_emotes):
        self.mock_globals.globalFfzEmotesCache = self.now
        self.mock_globals.globalFfzEmotes = {}
        emotes_ = {1: 'ZreknarF'}
        mock_emotes.return_value = emotes_
        await emotes.refreshFfzGlobalEmotes(self.now)
        self.assertEqual(self.mock_globals.globalFfzEmotesCache, self.now)
        self.assertEqual(self.mock_globals.globalFfzEmotes, {})
        self.assertFalse(mock_emotes.called)

    @patch('lib.api.ffz.getGlobalEmotes')
    async def test_ffz_global_none(self, mock_emotes):
        self.mock_globals.globalFfzEmotesCache = self.now
        self.mock_globals.globalFfzEmotes = {}
        mock_emotes.return_value = None
        await emotes.refreshFfzGlobalEmotes(self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalFfzEmotesCache,
                         self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalFfzEmotes, {})
        mock_emotes.assert_called_once_with()

    async def test_ffz_broadcaster(self):
        timestamp = self.now + timedelta(hours=1)
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.ffzCache = self.now
        self.mock_globals.channels = {'botgotsthis': channel}
        await emotes.refreshFfzRandomBroadcasterEmotes(timestamp)
        channel.updateFfzEmotes.assert_called_once_with()

    async def test_ffz_broadcaster_recent(self):
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.ffzCache = self.now
        self.mock_globals.channels = {'botgotsthis': channel}
        await emotes.refreshFfzRandomBroadcasterEmotes(self.now)
        self.assertFalse(channel.updateFfzEmotes.called)

    async def test_ffz_broadcaster_priority(self):
        timestamp = self.now + timedelta(hours=1)
        bgtchannel = Mock(spec=Channel)
        bgtchannel.channel = 'botgotsthis'
        bgtchannel.isStreaming = False
        bgtchannel.ffzCache = self.now
        mgtchannel = Mock(spec=Channel)
        mgtchannel.channel = 'megotsthis'
        mgtchannel.isStreaming = True
        mgtchannel.ffzCache = self.now
        self.mock_globals.channels = {'botgotsthis': bgtchannel,
                                      'megotsthis': mgtchannel}
        await emotes.refreshFfzRandomBroadcasterEmotes(timestamp)
        mgtchannel.updateFfzEmotes.assert_called_once_with()
        self.assertFalse(bgtchannel.updateFfzEmotes.called)

    @patch('random.choice', autospec=True)
    async def test_ffz_broadcaster_onlyone(self, mock_choice):
        timestamp = self.now + timedelta(hours=1)
        bgtchannel = Mock(spec=Channel)
        bgtchannel.channel = 'botgotsthis'
        bgtchannel.isStreaming = False
        bgtchannel.ffzCache = self.now
        mgtchannel = Mock(spec=Channel)
        mgtchannel.channel = 'megotsthis'
        mgtchannel.isStreaming = False
        mgtchannel.ffzCache = self.now
        self.mock_globals.channels = {'botgotsthis': bgtchannel,
                                      'megotsthis': mgtchannel}
        mock_choice.return_value = bgtchannel
        await emotes.refreshFfzRandomBroadcasterEmotes(timestamp)
        bgtchannel.updateFfzEmotes.assert_called_once_with()
        self.assertFalse(mgtchannel.updateFfzEmotes.called)

    @patch('random.choice', autospec=True)
    async def test_ffz_broadcaster_empty(self, mock_choice):
        timestamp = self.now + timedelta(hours=1)
        self.mock_globals.channels = {}
        await emotes.refreshFfzRandomBroadcasterEmotes(timestamp)
        self.assertFalse(mock_choice.called)

    @patch(emotes.__name__ + '.refreshBttvGlobalEmotes')
    @patch(emotes.__name__ + '.refreshBttvRandomBroadcasterEmotes')
    async def test_bttv(self, mock_broadcaster, mock_global):
        await emotes.refreshBetterTwitchTvEmotes(self.now)
        mock_broadcaster.assert_called_once_with(self.now)
        mock_global.assert_called_once_with(self.now)

    @patch('lib.api.bttv.getGlobalEmotes')
    async def test_bttv_global(self, mock_emotes):
        self.mock_globals.globalBttvEmotesCache = self.now
        self.mock_globals.globalBttvEmotes = {}
        emotes_ = {'54fa925e01e468494b85b54d': 'OhMyGoodness'}
        mock_emotes.return_value = emotes_
        await emotes.refreshBttvGlobalEmotes(self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalBttvEmotesCache,
                         self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalBttvEmotes, emotes_)
        mock_emotes.assert_called_once_with()

    @patch('lib.api.bttv.getGlobalEmotes')
    async def test_bttv_global_recent(self, mock_emotes):
        self.mock_globals.globalBttvEmotesCache = self.now
        self.mock_globals.globalBttvEmotes = {}
        emotes_ = {'54fa925e01e468494b85b54d': 'OhMyGoodness'}
        mock_emotes.return_value = emotes_
        await emotes.refreshBttvGlobalEmotes(self.now)
        self.assertEqual(self.mock_globals.globalBttvEmotesCache, self.now)
        self.assertEqual(self.mock_globals.globalBttvEmotes, {})
        self.assertFalse(mock_emotes.called)

    @patch('lib.api.bttv.getGlobalEmotes')
    async def test_bttv_global_none(self, mock_emotes):
        self.mock_globals.globalBttvEmotesCache = self.now
        self.mock_globals.globalBttvEmotes = {}
        mock_emotes.return_value = None
        await emotes.refreshBttvGlobalEmotes(self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalBttvEmotesCache,
                         self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalBttvEmotes, {})
        mock_emotes.assert_called_once_with()

    async def test_bttv_broadcaster(self):
        timestamp = self.now + timedelta(hours=1)
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.bttvCache = self.now
        self.mock_globals.channels = {'botgotsthis': channel}
        await emotes.refreshBttvRandomBroadcasterEmotes(timestamp)
        channel.updateBttvEmotes.assert_called_once_with()

    async def test_bttv_broadcaster_recent(self):
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.bttvCache = self.now
        self.mock_globals.channels = {'botgotsthis': channel}
        await emotes.refreshBttvRandomBroadcasterEmotes(self.now)
        self.assertFalse(channel.updateBttvEmotes.called)

    async def test_bttv_broadcaster_priority(self):
        timestamp = self.now + timedelta(hours=1)
        bgtchannel = Mock(spec=Channel)
        bgtchannel.channel = 'botgotsthis'
        bgtchannel.isStreaming = False
        bgtchannel.bttvCache = self.now
        mgtchannel = Mock(spec=Channel)
        mgtchannel.channel = 'megotsthis'
        mgtchannel.isStreaming = True
        mgtchannel.bttvCache = self.now
        self.mock_globals.channels = {'botgotsthis': bgtchannel,
                                      'megotsthis': mgtchannel}
        await emotes.refreshBttvRandomBroadcasterEmotes(timestamp)
        mgtchannel.updateBttvEmotes.assert_called_once_with()
        self.assertFalse(bgtchannel.updateBttvEmotes.called)

    @patch('random.choice', autospec=True)
    async def test_bttv_broadcaster_onlyone(self, mock_choice):
        timestamp = self.now + timedelta(hours=1)
        bgtchannel = Mock(spec=Channel)
        bgtchannel.channel = 'botgotsthis'
        bgtchannel.isStreaming = False
        bgtchannel.bttvCache = self.now
        mgtchannel = Mock(spec=Channel)
        mgtchannel.channel = 'megotsthis'
        mgtchannel.isStreaming = False
        mgtchannel.bttvCache = self.now
        self.mock_globals.channels = {'botgotsthis': bgtchannel,
                                      'megotsthis': mgtchannel}
        mock_choice.return_value = bgtchannel
        await emotes.refreshBttvRandomBroadcasterEmotes(timestamp)
        bgtchannel.updateBttvEmotes.assert_called_once_with()
        self.assertFalse(mgtchannel.updateBttvEmotes.called)

    @patch('random.choice', autospec=True)
    async def test_bttv_broadcaster_empty(self, mock_choice):
        timestamp = self.now + timedelta(hours=1)
        self.mock_globals.channels = {}
        await emotes.refreshBttvRandomBroadcasterEmotes(timestamp)
        self.assertFalse(mock_choice.called)
