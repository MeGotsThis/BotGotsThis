import unittest
from bot.data import Channel
from datetime import datetime, timedelta
from source.public.tasks import emotes
from unittest.mock import Mock, patch


class TestTasksEmotes(unittest.TestCase):
    def setUp(self):
        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()

        self.now = datetime(2000, 1, 1)

    @patch('source.api.twitch.twitch_emotes', autospec=True)
    def test_twitch(self, mock_emotes):
        self.mock_globals.globalEmotesCache = self.now
        self.mock_globals.globalEmotes = {}
        self.mock_globals.globalEmoteSets = {}
        emotes_ = {25: 'Kappa'}
        emotesets = {25: 0}
        mock_emotes.return_value = emotes_, emotesets
        emotes.refreshTwitchGlobalEmotes(self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalEmotesCache,
                         self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalEmotes, emotes_)
        self.assertEqual(self.mock_globals.globalEmoteSets, emotesets)
        mock_emotes.assert_called_once_with()

    @patch('source.api.twitch.twitch_emotes', autospec=True)
    def test_twitch_recent(self, mock_emotes):
        self.mock_globals.globalEmotesCache = self.now
        self.mock_globals.globalEmotes = {}
        self.mock_globals.globalEmoteSets = {}
        emotes_ = {25: 'Kappa'}
        emotesets = {25: 0}
        mock_emotes.return_value = emotes_, emotesets
        emotes.refreshTwitchGlobalEmotes(self.now)
        self.assertEqual(self.mock_globals.globalEmotesCache, self.now)
        self.assertEqual(self.mock_globals.globalEmotes, {})
        self.assertEqual(self.mock_globals.globalEmoteSets, {})
        self.assertFalse(mock_emotes.called)

    @patch('source.api.twitch.twitch_emotes', autospec=True)
    def test_twitch_none(self, mock_emotes):
        self.mock_globals.globalEmotesCache = self.now
        self.mock_globals.globalEmotes = {}
        self.mock_globals.globalEmoteSets = {}
        mock_emotes.return_value = None
        emotes.refreshTwitchGlobalEmotes(self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalEmotesCache,
                         self.now + timedelta(minutes=1))
        self.assertEqual(self.mock_globals.globalEmotes, {})
        self.assertEqual(self.mock_globals.globalEmoteSets, {})
        mock_emotes.assert_called_once_with()

    @patch('source.public.tasks.emotes.refreshFfzGlobalEmotes',
           autospec=True)
    @patch('source.public.tasks.emotes.refreshFfzRandomBroadcasterEmotes',
           autospec=True)
    def test_ffz(self, mock_broadcaster, mock_global):
        emotes.refreshFrankerFaceZEmotes(self.now)
        mock_broadcaster.assert_called_once_with(self.now)
        mock_global.assert_called_once_with(self.now)

    @patch('source.api.ffz.getGlobalEmotes', autospec=True)
    def test_ffz_global(self, mock_emotes):
        self.mock_globals.globalFfzEmotesCache = self.now
        self.mock_globals.globalFfzEmotes = {}
        emotes_ = {1: 'ZreknarF'}
        mock_emotes.return_value = emotes_
        emotes.refreshFfzGlobalEmotes(self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalFfzEmotesCache,
                         self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalFfzEmotes, emotes_)
        mock_emotes.assert_called_once_with()

    @patch('source.api.ffz.getGlobalEmotes', autospec=True)
    def test_ffz_global_recent(self, mock_emotes):
        self.mock_globals.globalFfzEmotesCache = self.now
        self.mock_globals.globalFfzEmotes = {}
        emotes_ = {1: 'ZreknarF'}
        mock_emotes.return_value = emotes_
        emotes.refreshFfzGlobalEmotes(self.now)
        self.assertEqual(self.mock_globals.globalFfzEmotesCache, self.now)
        self.assertEqual(self.mock_globals.globalFfzEmotes, {})
        self.assertFalse(mock_emotes.called)

    @patch('source.api.ffz.getGlobalEmotes', autospec=True)
    def test_ffz_global_none(self, mock_emotes):
        self.mock_globals.globalFfzEmotesCache = self.now
        self.mock_globals.globalFfzEmotes = {}
        mock_emotes.return_value = None
        emotes.refreshFfzGlobalEmotes(self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalFfzEmotesCache,
                         self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalFfzEmotes, {})
        mock_emotes.assert_called_once_with()

    def test_ffz_broadcaster(self):
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.ffzCache = self.now
        self.mock_globals.channels = {'botgotsthis': channel}
        emotes.refreshFfzRandomBroadcasterEmotes(self.now + timedelta(hours=1))
        channel.updateFfzEmotes.assert_called_once_with()

    def test_ffz_broadcaster_recent(self):
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.ffzCache = self.now
        self.mock_globals.channels = {'botgotsthis': channel}
        emotes.refreshFfzRandomBroadcasterEmotes(self.now)
        self.assertFalse(channel.updateFfzEmotes.called)

    def test_ffz_broadcaster_priority(self):
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
        emotes.refreshFfzRandomBroadcasterEmotes(self.now + timedelta(hours=1))
        mgtchannel.updateFfzEmotes.assert_called_once_with()
        self.assertFalse(bgtchannel.updateFfzEmotes.called)

    @patch('random.choice', autospec=True)
    def test_ffz_broadcaster_onlyone(self, mock_choice):
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
        emotes.refreshFfzRandomBroadcasterEmotes(self.now + timedelta(hours=1))
        bgtchannel.updateFfzEmotes.assert_called_once_with()
        self.assertFalse(mgtchannel.updateFfzEmotes.called)

    @patch('random.choice', autospec=True)
    def test_ffz_broadcaster_empty(self, mock_choice):
        self.mock_globals.channels = {}
        emotes.refreshFfzRandomBroadcasterEmotes(self.now + timedelta(hours=1))
        self.assertFalse(mock_choice.called)

    @patch('source.public.tasks.emotes.refreshBttvGlobalEmotes',
           autospec=True)
    @patch('source.public.tasks.emotes.refreshBttvRandomBroadcasterEmotes',
           autospec=True)
    def test_bttv(self, mock_broadcaster, mock_global):
        emotes.refreshBetterTwitchTvEmotes(self.now)
        mock_broadcaster.assert_called_once_with(self.now)
        mock_global.assert_called_once_with(self.now)

    @patch('source.api.bttv.getGlobalEmotes', autospec=True)
    def test_bttv_global(self, mock_emotes):
        self.mock_globals.globalBttvEmotesCache = self.now
        self.mock_globals.globalBttvEmotes = {}
        emotes_ = {'54fa925e01e468494b85b54d': 'OhMyGoodness'}
        mock_emotes.return_value = emotes_
        emotes.refreshBttvGlobalEmotes(self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalBttvEmotesCache,
                         self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalBttvEmotes, emotes_)
        mock_emotes.assert_called_once_with()

    @patch('source.api.bttv.getGlobalEmotes', autospec=True)
    def test_bttv_global_recent(self, mock_emotes):
        self.mock_globals.globalBttvEmotesCache = self.now
        self.mock_globals.globalBttvEmotes = {}
        emotes_ = {'54fa925e01e468494b85b54d': 'OhMyGoodness'}
        mock_emotes.return_value = emotes_
        emotes.refreshBttvGlobalEmotes(self.now)
        self.assertEqual(self.mock_globals.globalBttvEmotesCache, self.now)
        self.assertEqual(self.mock_globals.globalBttvEmotes, {})
        self.assertFalse(mock_emotes.called)

    @patch('source.api.bttv.getGlobalEmotes', autospec=True)
    def test_bttv_global_none(self, mock_emotes):
        self.mock_globals.globalBttvEmotesCache = self.now
        self.mock_globals.globalBttvEmotes = {}
        mock_emotes.return_value = None
        emotes.refreshBttvGlobalEmotes(self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalBttvEmotesCache,
                         self.now + timedelta(hours=1))
        self.assertEqual(self.mock_globals.globalBttvEmotes, {})
        mock_emotes.assert_called_once_with()

    def test_bttv_broadcaster(self):
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.bttvCache = self.now
        self.mock_globals.channels = {'botgotsthis': channel}
        emotes.refreshBttvRandomBroadcasterEmotes(self.now + timedelta(hours=1))
        channel.updateBttvEmotes.assert_called_once_with()

    def test_bttv_broadcaster_recent(self):
        channel = Mock(spec=Channel)
        channel.channel = 'botgotsthis'
        channel.isStreaming = False
        channel.bttvCache = self.now
        self.mock_globals.channels = {'botgotsthis': channel}
        emotes.refreshBttvRandomBroadcasterEmotes(self.now)
        self.assertFalse(channel.updateBttvEmotes.called)

    def test_bttv_broadcaster_priority(self):
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
        emotes.refreshBttvRandomBroadcasterEmotes(self.now + timedelta(hours=1))
        mgtchannel.updateBttvEmotes.assert_called_once_with()
        self.assertFalse(bgtchannel.updateBttvEmotes.called)

    @patch('random.choice', autospec=True)
    def test_bttv_broadcaster_onlyone(self, mock_choice):
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
        emotes.refreshBttvRandomBroadcasterEmotes(self.now + timedelta(hours=1))
        bgtchannel.updateBttvEmotes.assert_called_once_with()
        self.assertFalse(mgtchannel.updateBttvEmotes.called)

    @patch('random.choice', autospec=True)
    def test_bttv_broadcaster_empty(self, mock_choice):
        self.mock_globals.channels = {}
        emotes.refreshBttvRandomBroadcasterEmotes(self.now + timedelta(hours=1))
        self.assertFalse(mock_choice.called)
