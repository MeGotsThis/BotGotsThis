import unittest
from bot.data import Channel, Socket
from datetime import datetime, timedelta
from source.database import DatabaseBase
from source.public.tasks import twitch
from source.api.twitch import TwitchStatus
from unittest.mock import MagicMock, Mock, PropertyMock, call, patch

class TestTasksTwitchBase(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)

        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'

        patcher = patch('source.public.tasks.twitch.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.channels = {'botgotsthis': self.channel}


class TestTasksTwitch(TestTasksTwitchBase):
    def setUp(self):
        super().setUp()

        self.cache_property = PropertyMock(return_value=self.now)
        type(self.channel).twitchCache = self.cache_property

        self.streaming_property = PropertyMock(return_value=None)
        type(self.channel).streamingSince = self.streaming_property

        self.status_property = PropertyMock(return_value=None)
        type(self.channel).twitchStatus = self.status_property

        self.game_property = PropertyMock(return_value=None)
        type(self.channel).twitchGame = self.game_property

    @patch('source.public.tasks.twitch.twitch.active_streams')
    def test_streams_empty(self, mock_active):
        self.mock_globals.channels = {}
        twitch.checkStreamsAndChannel(self.now)
        self.assertFalse(mock_active.called)

    @patch('source.public.tasks.twitch.twitch.active_streams')
    def test_streams_none(self, mock_active):
        mock_active.return_value = None
        twitch.checkStreamsAndChannel(self.now)
        self.assertTrue(mock_active.called)
        self.assertFalse(self.cache_property.called)
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)

    @patch('source.public.tasks.twitch.twitch.active_streams')
    def test_streams(self, mock_active):
        streamed = datetime(1999, 1, 1)
        mock_active.return_value = {
            'botgotsthis': TwitchStatus(streamed, 'Kappa', 'Creative')
            }
        twitch.checkStreamsAndChannel(self.now)
        self.assertTrue(mock_active.called)
        self.cache_property.assert_called_once_with(self.now)
        self.streaming_property.assert_called_once_with(streamed)
        self.status_property.assert_called_once_with('Kappa')
        self.game_property.assert_called_once_with('Creative')

    @patch('source.public.tasks.twitch.twitch.active_streams')
    def test_streams_offline(self, mock_active):
        streamed = datetime(1999, 1, 1)
        mock_active.return_value = {}
        twitch.checkStreamsAndChannel(self.now)
        self.assertTrue(mock_active.called)
        self.assertFalse(self.cache_property.called)
        self.streaming_property.assert_called_once_with(None)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)

    @patch('source.public.tasks.twitch.twitch.channel_properties')
    def test_offline_empty(self, mock_channel):
        self.mock_globals.channels = {}
        twitch.checkOfflineChannels(self.now)
        self.assertFalse(mock_channel.called)
        self.assertFalse(self.cache_property.called)
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)

    @patch('source.public.tasks.twitch.twitch.channel_properties')
    def test_offline_streaming(self, mock_channel):
        self.channel.isStreaming = True
        self.cache_property.return_value = self.now - timedelta(hours=1)
        twitch.checkOfflineChannels(self.now)
        self.assertFalse(mock_channel.called)
        self.assertFalse(self.cache_property.called)
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)

    @patch('source.public.tasks.twitch.twitch.channel_properties')
    def test_offline_recent(self, mock_channel):
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now
        twitch.checkOfflineChannels(self.now)
        self.assertFalse(mock_channel.called)
        self.cache_property.assert_called_once_with()
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)

    @patch('source.public.tasks.twitch.twitch.channel_properties')
    def test_offline_none(self, mock_channel):
        mock_channel.return_value = None
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now - timedelta(hours=1)
        twitch.checkOfflineChannels(self.now)
        mock_channel.assert_called_once_with('botgotsthis')
        self.cache_property.assert_called_once_with()
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)

    @patch('source.public.tasks.twitch.twitch.channel_properties')
    def test_offline(self, mock_channel):
        mock_channel.return_value = TwitchStatus(None, 'Keepo', 'Music')
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now - timedelta(hours=1)
        twitch.checkOfflineChannels(self.now)
        mock_channel.assert_called_once_with('botgotsthis')
        self.cache_property.assert_has_calls([call(), call(self.now)])
        self.streaming_property.assert_called_once_with(None)
        self.status_property.assert_called_once_with('Keepo')
        self.game_property.assert_called_once_with('Music')


class TestTasksTwitchChatServer(TestTasksTwitchBase):
    def setUp(self):
        super().setUp()

        self.socket1 = Mock(spec=Socket)
        self.socket2 = Mock(spec=Socket)

        self.check_property = PropertyMock(return_value=self.now)
        type(self.channel).serverCheck = self.check_property

        self.socket_property = PropertyMock(return_value=self.socket1)
        type(self.channel).socket = self.socket_property

        patcher = patch('source.public.tasks.twitch.getDatabase')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()

        self.database = MagicMock(spec=DatabaseBase)
        self.mock_database.return_value.__enter__.return_value = self.database

        patcher = patch('source.public.tasks.twitch.twitch.chat_server')
        self.addCleanup(patcher.stop)
        self.mock_chatserver = patcher.start()

        patcher = patch('source.public.tasks.twitch.utils.ensureServer')
        self.addCleanup(patcher.stop)
        self.mock_ensureserver = patcher.start()

        self.mock_globals.clusters = {'twitch': self.socket1,
                                      'aws': self.socket2
                                      }

    def test_empty(self):
        self.mock_globals.channels = {}
        twitch.checkChatServers(self.now + timedelta(hours=1))
        self.assertFalse(self.mock_chatserver.called)
        self.assertFalse(self.mock_database.called)
        self.assertFalse(self.mock_ensureserver.called)

    def test_recent(self):
        twitch.checkChatServers(self.now)
        self.assertFalse(self.mock_chatserver.called)
        self.assertFalse(self.mock_database.called)
        self.assertFalse(self.mock_ensureserver.called)

    def test_none(self):
        self.mock_chatserver.return_value = None
        twitch.checkChatServers(self.now + timedelta(hours=1))
        self.check_property.assert_has_calls(
            [call(), call(self.now + timedelta(hours=1))])
        self.mock_chatserver.assert_called_once_with('botgotsthis')
        self.assertFalse(self.mock_database.called)
        self.assertFalse(self.mock_ensureserver.called)

    def test_same_cluster(self):
        self.mock_chatserver.return_value = 'twitch'
        twitch.checkChatServers(self.now + timedelta(hours=1))
        self.check_property.assert_has_calls(
            [call(), call(self.now + timedelta(hours=1))])
        self.mock_chatserver.assert_called_once_with('botgotsthis')
        self.assertFalse(self.mock_database.called)
        self.assertFalse(self.mock_ensureserver.called)

    def test_unknown_cluster(self):
        self.mock_chatserver.return_value = 'where is this'
        twitch.checkChatServers(self.now + timedelta(hours=1))
        self.check_property.assert_has_calls(
            [call(), call(self.now + timedelta(hours=1))])
        self.mock_chatserver.assert_called_once_with('botgotsthis')
        self.assertTrue(self.mock_database.called)
        self.assertTrue(self.database.getAutoJoinsPriority.called)
        self.assertTrue(self.database.setAutoJoinServer.called)
        self.assertTrue(self.mock_ensureserver.called)

    def test_different_cluster(self):
        self.mock_chatserver.return_value = 'aws'
        twitch.checkChatServers(self.now + timedelta(hours=1))
        self.check_property.assert_has_calls(
            [call(), call(self.now + timedelta(hours=1))])
        self.mock_chatserver.assert_called_once_with('botgotsthis')
        self.assertTrue(self.mock_database.called)
        self.assertTrue(self.database.getAutoJoinsPriority.called)
        self.assertTrue(self.database.setAutoJoinServer.called)
        self.assertTrue(self.mock_ensureserver.called)
