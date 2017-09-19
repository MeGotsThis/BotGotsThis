import asynctest

from bot.coroutine.connection import ConnectionHandler
from bot.data import Channel
from datetime import datetime, timedelta
from source.database import DatabaseMain
from pkg.botgotsthis.tasks import twitch
from source.api.twitch import TwitchCommunity, TwitchStatus
from asynctest.mock import MagicMock, Mock, PropertyMock, call, patch


class TestTasksTwitchBase(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)

        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.channels = {'botgotsthis': self.channel}
        self.mock_globals.globalSessionData = {}


class TestTasksTwitchIds(TestTasksTwitchBase):
    def setUp(self):
        super().setUp()

        self.mock_globals.twitchId = {}
        self.mock_globals.twitchIdName = {}
        self.mock_globals.twitchIdCache = {}

        patcher = patch('bot.utils.saveTwitchId', autospec=True)
        self.mock_save = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch('source.api.twitch.getTwitchIds')
        self.addCleanup(patcher.stop)
        self.mock_twitchid = patcher.start()
        self.mock_twitchid.return_value = {}

    async def test_empty(self):
        self.mock_globals.channels = {}
        await twitch.checkTwitchIds(self.now)
        self.assertFalse(self.mock_twitchid.called)
        self.assertFalse(self.mock_save.called)

    async def test_none(self):
        self.mock_twitchid.return_value = None
        await twitch.checkTwitchIds(self.now)
        self.assertTrue(self.mock_twitchid.called)
        self.assertFalse(self.mock_save.called)

    async def test(self):
        self.mock_twitchid.return_value = {'botgotsthis': '1'}
        await twitch.checkTwitchIds(self.now)
        self.assertTrue(self.mock_twitchid.called)
        self.mock_twitchid.assert_called_once_with(['botgotsthis'])
        self.mock_save.assert_called_once_with('botgotsthis', '1', self.now)

    async def test_multiple(self):
        mgtChannel = Mock(spec=Channel)
        mgtChannel.channel = 'botgotsthis'
        self.mock_globals.channels['megotsthis'] = mgtChannel
        self.mock_globals.twitchId = {'botgotsthis': '1'}
        self.mock_globals.twitchIdName = {'1': 'botgotsthis'}
        self.mock_globals.twitchIdCache = {'botgotsthis': self.now}
        self.mock_twitchid.return_value = {'megotsthis': '2'}
        await twitch.checkTwitchIds(self.now)
        self.mock_twitchid.assert_called_once_with(['megotsthis'])
        self.mock_save.assert_called_once_with('megotsthis', '2', self.now)

    async def test_recent(self):
        self.mock_globals.twitchId = {'botgotsthis': '1'}
        self.mock_globals.twitchIdName = {'1': 'botgotsthis'}
        self.mock_globals.twitchIdCache = {'botgotsthis': self.now}
        self.mock_twitchid.return_value = {'botgotsthis': '1'}
        await twitch.checkTwitchIds(self.now)
        self.assertFalse(self.mock_twitchid.called)
        self.assertFalse(self.mock_save.called)

    async def test_no_id(self):
        self.mock_twitchid.return_value = {}
        await twitch.checkTwitchIds(self.now)
        self.assertTrue(self.mock_twitchid.called)
        self.mock_save.assert_called_once_with('botgotsthis', None, self.now)

    async def test_cache_expired(self):
        self.mock_globals.twitchId = {'botgotsthis': '1'}
        self.mock_globals.twitchIdName = {'1': 'botgotsthis'}
        self.mock_globals.twitchIdCache = {
            'botgotsthis': self.now - timedelta(days=1)}
        self.mock_twitchid.return_value = {'botgotsthis': '1'}
        await twitch.checkTwitchIds(self.now)
        self.assertTrue(self.mock_twitchid.called)
        self.mock_save.assert_called_once_with('botgotsthis', '1', self.now)

    async def test_cache_expired_none(self):
        self.mock_globals.twitchId = {'botgotsthis': None}
        self.mock_globals.twitchIdName = {'1': 'botgotsthis'}
        self.mock_globals.twitchIdCache = {
            'botgotsthis': self.now - timedelta(hours=1)}
        self.mock_twitchid.return_value = {'botgotsthis': '1'}
        await twitch.checkTwitchIds(self.now)
        self.assertTrue(self.mock_twitchid.called)
        self.mock_save.assert_called_once_with('botgotsthis', '1', self.now)


class TestTasksTwitchStreams(TestTasksTwitchBase):
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

    @patch('source.api.twitch.active_streams')
    async def test_streams_empty(self, mock_active):
        self.mock_globals.channels = {}
        await twitch.checkStreamsAndChannel(self.now)
        self.assertFalse(mock_active.called)

    @patch('source.api.twitch.active_streams')
    async def test_streams_none(self, mock_active):
        mock_active.return_value = None
        await twitch.checkStreamsAndChannel(self.now)
        self.assertTrue(mock_active.called)
        self.assertFalse(self.cache_property.called)
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)

    @patch('source.api.twitch.active_streams')
    async def test_streams(self, mock_active):
        streamed = datetime(1999, 1, 1)
        mock_active.return_value = {
            'botgotsthis': TwitchStatus(streamed, 'Kappa', 'Creative', [])
            }
        await twitch.checkStreamsAndChannel(self.now)
        self.assertTrue(mock_active.called)
        self.cache_property.assert_called_once_with(self.now)
        self.streaming_property.assert_called_once_with(streamed)
        self.status_property.assert_called_once_with('Kappa')
        self.game_property.assert_called_once_with('Creative')

    @patch('source.api.twitch.active_streams')
    async def test_streams_offline(self, mock_active):
        mock_active.return_value = {}
        await twitch.checkStreamsAndChannel(self.now)
        self.assertTrue(mock_active.called)
        self.assertFalse(self.cache_property.called)
        self.streaming_property.assert_called_once_with(None)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)

    @patch('bot.utils.saveTwitchCommunity')
    @patch('source.api.twitch.channel_community')
    @patch('source.api.twitch.channel_properties')
    async def test_offline_empty(self, mock_channel, mock_community,
                                 mock_save):
        self.mock_globals.channels = {}
        await twitch.checkOfflineChannels(self.now)
        self.assertFalse(mock_channel.called)
        self.assertFalse(self.cache_property.called)
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)
        self.assertFalse(mock_community.called)
        self.assertFalse(mock_save.called)

    @patch('bot.utils.saveTwitchCommunity')
    @patch('source.api.twitch.channel_community')
    @patch('source.api.twitch.channel_properties')
    async def test_offline_streaming(self, mock_channel, mock_community,
                                     mock_save):
        self.channel.isStreaming = True
        self.cache_property.return_value = self.now - timedelta(hours=1)
        await twitch.checkOfflineChannels(self.now)
        self.assertFalse(mock_channel.called)
        self.assertFalse(self.cache_property.called)
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)
        self.assertFalse(mock_community.called)
        self.assertFalse(mock_save.called)

    @patch('bot.utils.saveTwitchCommunity')
    @patch('source.api.twitch.channel_community')
    @patch('source.api.twitch.channel_properties')
    async def test_offline_recent(self, mock_channel, mock_community,
                                  mock_save):
        mock_community.return_value = None
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now
        await twitch.checkOfflineChannels(self.now)
        self.assertFalse(mock_channel.called)
        self.cache_property.assert_called_once_with()
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)
        self.assertFalse(mock_community.called)
        self.assertFalse(mock_save.called)

    @patch('bot.utils.saveTwitchCommunity')
    @patch('source.api.twitch.channel_community')
    @patch('source.api.twitch.channel_properties')
    async def test_offline_none(self, mock_channel, mock_community, mock_save):
        mock_community.return_value = None
        mock_channel.return_value = None
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now - timedelta(hours=1)
        await twitch.checkOfflineChannels(self.now)
        mock_channel.assert_called_once_with('botgotsthis')
        self.cache_property.assert_has_calls(
            [call(), call(self.now),
             call(self.now - timedelta(seconds=240))])
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)
        self.assertFalse(mock_community.called)
        self.assertFalse(mock_save.called)

    @patch('bot.utils.saveTwitchCommunity')
    @patch('source.api.twitch.channel_community')
    @patch('source.api.twitch.channel_properties')
    async def test_offline(self, mock_channel, mock_community, mock_save):
        mock_community.return_value = None
        mock_channel.return_value = TwitchStatus(None, 'Keepo', 'Music', None)
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now - timedelta(hours=1)
        await twitch.checkOfflineChannels(self.now)
        mock_channel.assert_called_once_with('botgotsthis')
        self.cache_property.assert_has_calls([call(), call(self.now)])
        self.streaming_property.assert_called_once_with(None)
        self.status_property.assert_called_once_with('Keepo')
        self.game_property.assert_called_once_with('Music')
        mock_community.assert_called_once_with('botgotsthis')
        self.assertFalse(mock_save.called)

    @patch('bot.utils.saveTwitchCommunity')
    @patch('source.api.twitch.channel_community')
    @patch('source.api.twitch.channel_properties')
    async def test_offline_community_empty(self, mock_channel, mock_community,
                                           mock_save):
        mock_community.return_value = []
        mock_channel.return_value = TwitchStatus(None, 'Keepo', 'Music', None)
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now - timedelta(hours=1)
        await twitch.checkOfflineChannels(self.now)
        mock_channel.assert_called_once_with('botgotsthis')
        self.cache_property.assert_has_calls([call(), call(self.now)])
        self.streaming_property.assert_called_once_with(None)
        self.status_property.assert_called_once_with('Keepo')
        self.game_property.assert_called_once_with('Music')
        mock_community.assert_called_once_with('botgotsthis')
        self.assertFalse(mock_save.called)

    @patch('bot.utils.saveTwitchCommunity')
    @patch('source.api.twitch.channel_community')
    @patch('source.api.twitch.channel_properties')
    async def test_offline_community(self, mock_channel, mock_community,
                                     mock_save):
        mock_community.return_value = [TwitchCommunity('1', 'BotGotsThis')]
        mock_channel.return_value = TwitchStatus(None, 'Keepo', 'Music', None)
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now - timedelta(hours=1)
        await twitch.checkOfflineChannels(self.now)
        mock_channel.assert_called_once_with('botgotsthis')
        self.cache_property.assert_has_calls([call(), call(self.now)])
        self.streaming_property.assert_called_once_with(None)
        self.status_property.assert_called_once_with('Keepo')
        self.game_property.assert_called_once_with('Music')
        mock_community.assert_called_once_with('botgotsthis')
        mock_save.assert_called_once_with('BotGotsThis', '1', self.now)


class TestTasksTwitchChatServer(TestTasksTwitchBase):
    def setUp(self):
        super().setUp()

        self.connection1 = Mock(spec=ConnectionHandler)
        self.connection2 = Mock(spec=ConnectionHandler)

        self.check_property = PropertyMock(return_value=self.now)
        type(self.channel).serverCheck = self.check_property

        self.socket_property = PropertyMock(return_value=self.connection1)
        type(self.channel).connection = self.socket_property

        patcher = patch('source.database.get_database')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()

        self.database = MagicMock(spec=DatabaseMain)
        self.mock_database.return_value = self.database
        self.database.__aenter__.return_value = self.database

        patcher = patch('source.api.twitch.chat_server')
        self.addCleanup(patcher.stop)
        self.mock_chatserver = patcher.start()

        patcher = patch('bot.utils.ensureServer')
        self.addCleanup(patcher.stop)
        self.mock_ensureserver = patcher.start()

        self.mock_globals.clusters = {'twitch': self.connection1,
                                      'aws': self.connection2
                                      }

    async def test_empty(self):
        self.mock_globals.channels = {}
        await twitch.checkChatServers(self.now + timedelta(hours=1))
        self.assertFalse(self.mock_chatserver.called)
        self.assertFalse(self.mock_database.called)
        self.assertFalse(self.mock_ensureserver.called)

    async def test_recent(self):
        await twitch.checkChatServers(self.now)
        self.assertFalse(self.mock_chatserver.called)
        self.assertFalse(self.mock_database.called)
        self.assertFalse(self.mock_ensureserver.called)

    async def test_none(self):
        self.mock_chatserver.return_value = None
        await twitch.checkChatServers(self.now + timedelta(hours=1))
        self.check_property.assert_has_calls(
            [call(), call(self.now + timedelta(hours=1))])
        self.mock_chatserver.assert_called_once_with('botgotsthis')
        self.assertFalse(self.mock_database.called)
        self.assertFalse(self.mock_ensureserver.called)

    async def test_same_cluster(self):
        self.mock_chatserver.return_value = 'twitch'
        await twitch.checkChatServers(self.now + timedelta(hours=1))
        self.check_property.assert_has_calls(
            [call(), call(self.now + timedelta(hours=1))])
        self.mock_chatserver.assert_called_once_with('botgotsthis')
        self.assertFalse(self.mock_database.called)
        self.assertFalse(self.mock_ensureserver.called)

    async def test_unknown_cluster(self):
        self.mock_chatserver.return_value = 'where is this'
        await twitch.checkChatServers(self.now + timedelta(hours=1))
        self.check_property.assert_has_calls(
            [call(), call(self.now + timedelta(hours=1))])
        self.mock_chatserver.assert_called_once_with('botgotsthis')
        self.assertTrue(self.mock_database.called)
        self.assertTrue(self.database.getAutoJoinsPriority.called)
        self.assertTrue(self.database.setAutoJoinServer.called)
        self.assertTrue(self.mock_ensureserver.called)

    async def test_different_cluster(self):
        self.mock_chatserver.return_value = 'aws'
        await twitch.checkChatServers(self.now + timedelta(hours=1))
        self.check_property.assert_has_calls(
            [call(), call(self.now + timedelta(hours=1))])
        self.mock_chatserver.assert_called_once_with('botgotsthis')
        self.assertTrue(self.mock_database.called)
        self.assertTrue(self.database.getAutoJoinsPriority.called)
        self.assertTrue(self.database.setAutoJoinServer.called)
        self.assertTrue(self.mock_ensureserver.called)
