import unittest
from bot.data import Channel
from datetime import datetime, timedelta
from source.public.tasks import emotes
from unittest.mock import Mock, patch


class TestTasksEmotes(unittest.TestCase):
    def setUp(self):
        patcher = patch('source.public.tasks.emotes.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()

    @patch('source.public.tasks.emotes.twitch.twitch_emotes', autospec=True)
    def test_twitch(self, mock_emotes):
        now = datetime(2000, 1, 1)
        self.mock_globals.globalEmotesCache = now
        self.mock_globals.globalEmotes = {}
        self.mock_globals.globalEmoteSets = {}
        emotes_ = {25: 'Kappa'}
        emotesets = {25: 0}
        mock_emotes.return_value = emotes_, emotesets
        emotes.refreshTwitchGlobalEmotes(now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalEmotesCache,
                         now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalEmotes, emotes_)
        self.assertEqual(self.mock_globals.globalEmoteSets, emotesets)
        mock_emotes.assert_called_once_with()

    @patch('source.public.tasks.emotes.twitch.twitch_emotes', autospec=True)
    def test_twitch_recent(self, mock_emotes):
        now = datetime(2000, 1, 1)
        self.mock_globals.globalEmotesCache = now
        self.mock_globals.globalEmotes = {}
        self.mock_globals.globalEmoteSets = {}
        emotes_ = {25: 'Kappa'}
        emotesets = {25: 0}
        mock_emotes.return_value = emotes_, emotesets
        emotes.refreshTwitchGlobalEmotes(now)
        self.assertEqual(self.mock_globals.globalEmotesCache, now)
        self.assertEqual(self.mock_globals.globalEmotes, {})
        self.assertEqual(self.mock_globals.globalEmoteSets, {})
        self.assertFalse(mock_emotes.called)

    @patch('source.public.tasks.emotes.twitch.twitch_emotes', autospec=True)
    def test_twitch_none(self, mock_emotes):
        now = datetime(2000, 1, 1)
        self.mock_globals.globalEmotesCache = now
        self.mock_globals.globalEmotes = {}
        self.mock_globals.globalEmoteSets = {}
        mock_emotes.return_value = None
        emotes.refreshTwitchGlobalEmotes(now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalEmotesCache,
                         now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalEmotes, {})
        self.assertEqual(self.mock_globals.globalEmoteSets, {})
        mock_emotes.assert_called_once_with()

    @patch('source.public.tasks.emotes.refreshFfzGlobalEmotes',
           autospec=True)
    @patch('source.public.tasks.emotes.refreshFfzRandomBroadcasterEmotes',
           autospec=True)
    def test_ffz(self, mock_broadcaster, mock_global):
        now = datetime(2000, 1, 1)
        emotes.refreshFrankerFaceZEmotes(now)
        mock_broadcaster.assert_called_once_with(now)
        mock_global.assert_called_once_with(now)

    @patch('source.public.tasks.emotes.ffz.getGlobalEmotes', autospec=True)
    def test_ffz_global(self, mock_emotes):
        now = datetime(2000, 1, 1)
        self.mock_globals.globalFfzEmotesCache = now
        self.mock_globals.globalFfzEmotes = {}
        emotes_ = {1: 'ZreknarF'}
        mock_emotes.return_value = emotes_
        emotes.refreshFfzGlobalEmotes(now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalFfzEmotesCache,
                         now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalFfzEmotes, emotes_)
        mock_emotes.assert_called_once_with()

    @patch('source.public.tasks.emotes.ffz.getGlobalEmotes', autospec=True)
    def test_ffz_global_recent(self, mock_emotes):
        now = datetime(2000, 1, 1)
        self.mock_globals.globalFfzEmotesCache = now
        self.mock_globals.globalFfzEmotes = {}
        emotes_ = {1: 'ZreknarF'}
        mock_emotes.return_value = emotes_
        emotes.refreshFfzGlobalEmotes(now)
        self.assertEqual(self.mock_globals.globalFfzEmotesCache, now)
        self.assertEqual(self.mock_globals.globalFfzEmotes, {})
        self.assertFalse(mock_emotes.called)

    @patch('source.public.tasks.emotes.ffz.getGlobalEmotes', autospec=True)
    def test_ffz_global_none(self, mock_emotes):
        now = datetime(2000, 1, 1)
        self.mock_globals.globalFfzEmotesCache = now
        self.mock_globals.globalFfzEmotes = {}
        mock_emotes.return_value = None
        emotes.refreshFfzGlobalEmotes(now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalFfzEmotesCache,
                         now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalFfzEmotes, {})
        mock_emotes.assert_called_once_with()

    def test_ffz_broadcaster(self):
        now = datetime(2000, 1, 1)
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.ffzCache = now
        self.mock_globals.channels = {'botgotsthis': channel}
        emotes.refreshFfzRandomBroadcasterEmotes(now + timedelta(hours=1))
        channel.updateFfzEmotes.assert_called_once_with()

    def test_ffz_broadcaster_recent(self):
        now = datetime(2000, 1, 1)
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.ffzCache = now
        self.mock_globals.channels = {'botgotsthis': channel}
        emotes.refreshFfzRandomBroadcasterEmotes(now)
        self.assertFalse(channel.updateFfzEmotes.called)

    def test_ffz_broadcaster_priority(self):
        now = datetime(2000, 1, 1)
        bgtchannel = Mock(spec=Channel)
        bgtchannel.channel = 'botgotsthis'
        bgtchannel.isStreaming = False
        bgtchannel.ffzCache = now
        mgtchannel = Mock(spec=Channel)
        mgtchannel.channel = 'megotsthis'
        mgtchannel.isStreaming = True
        mgtchannel.ffzCache = now
        self.mock_globals.channels = {'botgotsthis': bgtchannel,
                                      'megotsthis': mgtchannel}
        emotes.refreshFfzRandomBroadcasterEmotes(now + timedelta(hours=1))
        mgtchannel.updateFfzEmotes.assert_called_once_with()
        self.assertFalse(bgtchannel.updateFfzEmotes.called)

    @patch('source.public.tasks.emotes.random.choice', autospec=True)
    def test_ffz_broadcaster_onlyone(self, mock_choice):
        now = datetime(2000, 1, 1)
        bgtchannel = Mock(spec=Channel)
        bgtchannel.channel = 'botgotsthis'
        bgtchannel.isStreaming = False
        bgtchannel.ffzCache = now
        mgtchannel = Mock(spec=Channel)
        mgtchannel.channel = 'megotsthis'
        mgtchannel.isStreaming = False
        mgtchannel.ffzCache = now
        self.mock_globals.channels = {'botgotsthis': bgtchannel,
                                      'megotsthis': mgtchannel}
        mock_choice.return_value = bgtchannel
        emotes.refreshFfzRandomBroadcasterEmotes(now + timedelta(hours=1))
        bgtchannel.updateFfzEmotes.assert_called_once_with()
        self.assertFalse(mgtchannel.updateFfzEmotes.called)

    @patch('source.public.tasks.emotes.refreshBttvGlobalEmotes',
           autospec=True)
    @patch('source.public.tasks.emotes.refreshBttvRandomBroadcasterEmotes',
           autospec=True)
    def test_bttv(self, mock_broadcaster, mock_global):
        now = datetime(2000, 1, 1)
        emotes.refreshBetterTwitchTvEmotes(now)
        mock_broadcaster.assert_called_once_with(now)
        mock_global.assert_called_once_with(now)

    @patch('source.public.tasks.emotes.bttv.getGlobalEmotes', autospec=True)
    def test_bttv_global(self, mock_emotes):
        now = datetime(2000, 1, 1)
        self.mock_globals.globalBttvEmotesCache = now
        self.mock_globals.globalBttvEmotes = {}
        emotes_ = {'54fa925e01e468494b85b54d': 'OhMyGoodness'}
        mock_emotes.return_value = emotes_
        emotes.refreshBttvGlobalEmotes(now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalBttvEmotesCache,
                         now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalBttvEmotes, emotes_)
        mock_emotes.assert_called_once_with()

    @patch('source.public.tasks.emotes.bttv.getGlobalEmotes', autospec=True)
    def test_bttv_global_recent(self, mock_emotes):
        now = datetime(2000, 1, 1)
        self.mock_globals.globalBttvEmotesCache = now
        self.mock_globals.globalBttvEmotes = {}
        emotes_ = {'54fa925e01e468494b85b54d': 'OhMyGoodness'}
        mock_emotes.return_value = emotes_
        emotes.refreshBttvGlobalEmotes(now)
        self.assertEqual(self.mock_globals.globalBttvEmotesCache, now)
        self.assertEqual(self.mock_globals.globalBttvEmotes, {})
        self.assertFalse(mock_emotes.called)

    @patch('source.public.tasks.emotes.bttv.getGlobalEmotes', autospec=True)
    def test_bttv_global_none(self, mock_emotes):
        now = datetime(2000, 1, 1)
        self.mock_globals.globalBttvEmotesCache = now
        self.mock_globals.globalBttvEmotes = {}
        mock_emotes.return_value = None
        emotes.refreshBttvGlobalEmotes(now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalBttvEmotesCache,
                         now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalBttvEmotes, {})
        mock_emotes.assert_called_once_with()

    def test_bttv_broadcaster(self):
        now = datetime(2000, 1, 1)
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.bttvCache = now
        self.mock_globals.channels = {'botgotsthis': channel}
        emotes.refreshBttvRandomBroadcasterEmotes(now + timedelta(hours=1))
        channel.updateBttvEmotes.assert_called_once_with()

    def test_bttv_broadcaster_recent(self):
        now = datetime(2000, 1, 1)
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.bttvCache = now
        self.mock_globals.channels = {'botgotsthis': channel}
        emotes.refreshBttvRandomBroadcasterEmotes(now)
        self.assertFalse(channel.updateBttvEmotes.called)

    def test_bttv_broadcaster_priority(self):
        now = datetime(2000, 1, 1)
        bgtchannel = Mock(spec=Channel)
        bgtchannel.channel = 'botgotsthis'
        bgtchannel.isStreaming = False
        bgtchannel.bttvCache = now
        mgtchannel = Mock(spec=Channel)
        mgtchannel.channel = 'megotsthis'
        mgtchannel.isStreaming = True
        mgtchannel.bttvCache = now
        self.mock_globals.channels = {'botgotsthis': bgtchannel,
                                      'megotsthis': mgtchannel}
        emotes.refreshBttvRandomBroadcasterEmotes(now + timedelta(hours=1))
        mgtchannel.updateBttvEmotes.assert_called_once_with()
        self.assertFalse(bgtchannel.updateBttvEmotes.called)

    @patch('source.public.tasks.emotes.random.choice', autospec=True)
    def test_bttv_broadcaster_onlyone(self, mock_choice):
        now = datetime(2000, 1, 1)
        bgtchannel = Mock(spec=Channel)
        bgtchannel.channel = 'botgotsthis'
        bgtchannel.isStreaming = False
        bgtchannel.bttvCache = now
        mgtchannel = Mock(spec=Channel)
        mgtchannel.channel = 'megotsthis'
        mgtchannel.isStreaming = False
        mgtchannel.bttvCache = now
        self.mock_globals.channels = {'botgotsthis': bgtchannel,
                                      'megotsthis': mgtchannel}
        mock_choice.return_value = bgtchannel
        emotes.refreshBttvRandomBroadcasterEmotes(now + timedelta(hours=1))
        bgtchannel.updateBttvEmotes.assert_called_once_with()
        self.assertFalse(mgtchannel.updateBttvEmotes.called)
