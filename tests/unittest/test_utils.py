import unittest
import asynctest

from datetime import datetime, timedelta
from io import StringIO
from asynctest.mock import Mock, patch

from bot import utils
from bot.coroutine import connection
from bot.data import Channel, MessagingQueue
from source.api.twitch import TwitchCommunity
from tests.unittest.mock_class import StrContains


class TestUtils(unittest.TestCase):
    def test_now(self):
        self.assertIsInstance(utils.now(), datetime)

    @patch('bot.globals', autospec=True)
    def test_joinChannel_none(self, mock_globals):
        mock_globals.channels = {}
        mock_globals.clusters = {
            'aws': Mock(spec=connection.ConnectionHandler)
            }
        self.assertRaises(TypeError, utils.joinChannel, None)

    @patch('bot.globals', autospec=True)
    def test_joinChannel_nocluster(self, mock_globals):
        mock_globals.channels = {}
        mock_globals.clusters = {
            'twitch': Mock(spec=connection.ConnectionHandler)
            }
        self.assertIs(
            utils.joinChannel('botgotsthis', cluster='botgotsthis'), None)
        self.assertNotIn('botgotsthis', mock_globals.channels)

    @patch('bot.globals', autospec=True)
    def test_joinChannel_existing_channel(self, mock_globals):
        mock_globals.clusters = {
            'twitch': Mock(spec=connection.ConnectionHandler)
            }
        mock_globals.channels = {
            'botgotsthis': Channel('botgotsthis',
                                   mock_globals.clusters['twitch'], 1)
            }
        self.assertIs(
            utils.joinChannel('botgotsthis', 0, 'twitch'), False)
        self.assertIn('botgotsthis', mock_globals.channels)
        self.assertEqual(mock_globals.channels['botgotsthis'].joinPriority, 0)

    @patch('bot.globals', autospec=True)
    def test_joinChannel(self, mock_globals):
        mock_globals.channels = {}
        mock_globals.clusters = {
            'twitch': Mock(spec=connection.ConnectionHandler)
            }
        self.assertIs(utils.joinChannel('botgotsthis', 0, 'twitch'), True)
        self.assertIn('botgotsthis', mock_globals.channels)
        self.assertEqual(mock_globals.channels['botgotsthis'].joinPriority, 0)
        mock_globals.clusters['twitch'].join_channel.assert_called_once_with(
            mock_globals.channels['botgotsthis'])

    @patch('bot.globals', autospec=True)
    def test_partChannel_none(self, mock_globals):
        mock_globals.channels = {}
        self.assertRaises(TypeError, utils.partChannel, None)

    @patch('bot.globals', autospec=True)
    @patch.object(Channel, 'part', autospec=True)
    def test_partChannel_not_existing(self, mock_part, mock_globals):
        mock_globals.channels = {}
        utils.partChannel('botgotsthis')
        self.assertFalse(mock_part.called)

    @patch('bot.globals', autospec=True)
    def test_partChannel(self, mock_globals):
        channel = Mock(spec=Channel)
        mock_globals.channels = {
            'botgotsthis': channel
            }
        utils.partChannel('botgotsthis')
        channel.part.assert_called_once_with()

    @patch('bot.globals', autospec=True)
    def test_whisper(self, mock_globals):
        connection_ = Mock(spec=connection.ConnectionHandler)
        connection_.messaging = Mock(spec=MessagingQueue)
        mock_globals.clusters = {
            'twitch': connection_
            }
        mock_globals.whisperCluster = 'twitch'
        utils.whisper('botgotsthis', 'Kappa')
        connection_.messaging.sendWhisper.assert_called_once_with(
            'botgotsthis', 'Kappa')

    @patch('bot.globals', autospec=True)
    def test_clearAllChat(self, mock_globals):
        connection_ = Mock(spec=connection.ConnectionHandler)
        connection_.messaging = Mock(spec=MessagingQueue)
        mock_globals.clusters = {
            'twitch': connection_
            }
        utils.clearAllChat()
        connection_.messaging.clearAllChat.assert_called_once_with()

    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_saveTwitchId(self, mock_now, mock_globals):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchId = {}
        mock_globals.twitchIdName = {}
        mock_globals.twitchIdCache = {}
        utils.saveTwitchId('botgotsthis', '1')
        mock_now.assert_called_once_with()
        self.assertIn('botgotsthis', mock_globals.twitchId)
        self.assertIn('1', mock_globals.twitchIdName)
        self.assertIn('botgotsthis', mock_globals.twitchIdCache)
        self.assertEqual(mock_globals.twitchId['botgotsthis'], '1')
        self.assertEqual(mock_globals.twitchIdName['1'], 'botgotsthis')
        self.assertEqual(mock_globals.twitchIdCache['botgotsthis'], now)

    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_saveTwitchId_None(self, mock_now, mock_globals):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchId = {}
        mock_globals.twitchIdName = {}
        mock_globals.twitchIdCache = {}
        utils.saveTwitchId('botgotsthis', None)
        mock_now.assert_called_once_with()
        self.assertIn('botgotsthis', mock_globals.twitchId)
        self.assertNotIn(None, mock_globals.twitchIdName)
        self.assertIn('botgotsthis', mock_globals.twitchIdCache)
        self.assertIsNone(mock_globals.twitchId['botgotsthis'])
        self.assertEqual(mock_globals.twitchIdCache['botgotsthis'], now)

    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_saveTwitchId_timestamp(self, mock_now, mock_globals):
        now = datetime(2000, 1, 1)
        mock_globals.twitchId = {}
        mock_globals.twitchIdName = {}
        mock_globals.twitchIdCache = {}
        utils.saveTwitchId('botgotsthis', '1', now)
        self.assertFalse(mock_now.called)
        self.assertIn('botgotsthis', mock_globals.twitchId)
        self.assertIn('1', mock_globals.twitchIdName)
        self.assertIn('botgotsthis', mock_globals.twitchIdCache)
        self.assertEqual(mock_globals.twitchId['botgotsthis'], '1')
        self.assertEqual(mock_globals.twitchIdName['1'], 'botgotsthis')
        self.assertEqual(mock_globals.twitchIdCache['botgotsthis'], now)

    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_saveTwitchCommunity(self, mock_now, mock_globals):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {}
        mock_globals.twitchCommunityId = {}
        mock_globals.twitchCommunityCache = {}
        utils.saveTwitchCommunity('Speedrunning',
                                  '6e940c4a-c42f-47d2-af83-0a2c7e47c421')
        mock_now.assert_called_once_with()
        self.assertIn('speedrunning', mock_globals.twitchCommunity)
        self.assertIn('6e940c4a-c42f-47d2-af83-0a2c7e47c421',
                      mock_globals.twitchCommunityId)
        self.assertIn('speedrunning', mock_globals.twitchCommunityCache)
        self.assertEqual(mock_globals.twitchCommunity['speedrunning'],
                         '6e940c4a-c42f-47d2-af83-0a2c7e47c421')
        self.assertEqual(
            mock_globals.twitchCommunityId[
                '6e940c4a-c42f-47d2-af83-0a2c7e47c421'],
            'Speedrunning')
        self.assertEqual(mock_globals.twitchCommunityCache['speedrunning'],
                         now)

    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_saveTwitchCommunity_id_None(self, mock_now, mock_globals):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {}
        mock_globals.twitchCommunityId = {}
        mock_globals.twitchCommunityCache = {}
        utils.saveTwitchCommunity('Speedrunning', None)
        mock_now.assert_called_once_with()
        self.assertIn('speedrunning', mock_globals.twitchCommunity)
        self.assertNotIn(None, mock_globals.twitchCommunityId)
        self.assertIn('speedrunning', mock_globals.twitchCommunityCache)
        self.assertIsNone(mock_globals.twitchCommunity['speedrunning'])
        self.assertEqual(mock_globals.twitchCommunityCache['speedrunning'],
                         now)

    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_saveTwitchCommunity_name_None(self, mock_now, mock_globals):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {}
        mock_globals.twitchCommunityId = {}
        mock_globals.twitchCommunityCache = {}
        utils.saveTwitchCommunity(None, '6e940c4a-c42f-47d2-af83-0a2c7e47c421')
        mock_now.assert_called_once_with()
        self.assertNotIn(None, mock_globals.twitchCommunity)
        self.assertIn(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421',
            mock_globals.twitchCommunityId)
        self.assertNotIn(None, mock_globals.twitchCommunityCache)
        self.assertIsNone(
            mock_globals.twitchCommunityId[
                '6e940c4a-c42f-47d2-af83-0a2c7e47c421'])

    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_saveTwitchCommunity_timestamp(self, mock_now, mock_globals):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {}
        mock_globals.twitchCommunityId = {}
        mock_globals.twitchCommunityCache = {}
        utils.saveTwitchCommunity('Speedrunning',
                                  '6e940c4a-c42f-47d2-af83-0a2c7e47c421', now)
        self.assertFalse(mock_now.called)
        self.assertIn('speedrunning', mock_globals.twitchCommunity)
        self.assertIn('6e940c4a-c42f-47d2-af83-0a2c7e47c421',
                      mock_globals.twitchCommunityId)
        self.assertIn('speedrunning', mock_globals.twitchCommunityCache)
        self.assertEqual(mock_globals.twitchCommunity['speedrunning'],
                         '6e940c4a-c42f-47d2-af83-0a2c7e47c421')
        self.assertEqual(
            mock_globals.twitchCommunityId[
                '6e940c4a-c42f-47d2-af83-0a2c7e47c421'],
            'Speedrunning')
        self.assertEqual(mock_globals.twitchCommunityCache['speedrunning'],
                         now)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_print(self, mock_now, mock_config, mock_stdout):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.development = False
        utils.print('Kappa')
        self.assertEqual(mock_stdout.getvalue(), '')

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_print_development(self, mock_now, mock_config, mock_stdout):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.development = True
        utils.print('Kappa')
        self.assertEqual(mock_stdout.getvalue(), '2000-01-01 00:00:00 Kappa\n')

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_print_override(self, mock_now, mock_config, mock_stdout):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.development = False
        utils.print('Kappa', override=True)
        self.assertEqual(mock_stdout.getvalue(), '2000-01-01 00:00:00 Kappa\n')

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_print_override_dev(self, mock_now, mock_config, mock_stdout):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.development = True
        utils.print('Kappa', override=False)
        self.assertEqual(mock_stdout.getvalue(), '2000-01-01 00:00:00 Kappa\n')

    @patch('bot.coroutine.logging', autospec=True)
    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_print_file(self, mock_now, mock_config, mock_stdout,
                        mock_logging):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.development = False
        utils.print('Kappa', file=True)
        self.assertEqual(mock_stdout.getvalue(), '')
        mock_logging.log.assert_called_once_with(
            'output.log', '2000-01-01T00:00:00.000000 Kappa\n')

    @patch('bot.coroutine.logging', autospec=True)
    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_print_file_multiple(self, mock_now, mock_config, mock_stdout,
                                 mock_logging):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.development = False
        utils.print('Kappa', 'Kappa', file=True)
        self.assertEqual(mock_stdout.getvalue(), '')
        mock_logging.log.assert_called_once_with(
            'output.log', '2000-01-01T00:00:00.000000 Kappa Kappa\n')

    @patch('bot.coroutine.logging', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_logIrcMessage_config(self, mock_now, mock_config, mock_logging):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.ircLogFolder = 'log'
        utils.logIrcMessage('botgotsthis', 'Kappa')
        mock_logging.log.assert_called_once_with(
            StrContains('botgotsthis'), StrContains('Kappa'))

    @patch('bot.coroutine.logging', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_logIrcMessage_config_None(self, mock_now, mock_config,
                                       mock_logging):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.ircLogFolder = None
        utils.logIrcMessage('botgotsthis', 'Kappa')
        self.assertFalse(mock_logging.log.called)

    @patch('sys.stderr', new_callable=StringIO)
    @patch('bot.coroutine.logging', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_logException(self, mock_now, mock_config, mock_logging,
                          mock_stderr):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.development = True
        mock_config.exceptionLog = 'exception'
        try:
            raise Exception()
        except Exception:
            utils.logException()
        mock_logging.log.assert_called_once_with(
            StrContains('exception'),
            StrContains('2000', '01', 'Exception', __file__,
                        'test_logException', 'raise Exception'))
        self.assertEqual(mock_stderr.getvalue(),
                         StrContains('2000', '1', 'Exception', __file__,
                                     'test_logException', 'raise Exception'))

    @patch('sys.stderr', new_callable=StringIO)
    @patch('bot.coroutine.logging', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_logException_no_development(
            self, mock_now, mock_config, mock_logging, mock_stderr):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.development = False
        mock_config.exceptionLog = 'exception'
        try:
            raise Exception()
        except Exception:
            utils.logException()
        mock_logging.log.assert_called_once_with(
            StrContains('exception'),
            StrContains('2000', '1', 'Exception', __file__,
                        'test_logException', 'raise Exception'))
        self.assertEqual(mock_stderr.getvalue(), '')

    @patch('bot.coroutine.logging', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_logException_config_None(self, mock_now, mock_config,
                                      mock_logging):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.exceptionLog = None
        try:
            raise Exception()
        except Exception:
            utils.logException()
        self.assertFalse(mock_logging.log.called)


class TestUtilsAsync(asynctest.TestCase):
    @patch('source.api.twitch.getTwitchIds')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchId', autospec=True)
    async def test_loadTwitchId(self, mock_save, mock_now, mock_globals,
                                mock_getIds):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchId = {}
        mock_globals.twitchIdCache = {}
        mock_getIds.return_value = {'botgotsthis': '1'}
        self.assertTrue(await utils.loadTwitchId('botgotsthis'))
        mock_now.assert_called_once_with()
        mock_getIds.assert_called_once_with(['botgotsthis'])
        mock_save.assert_called_once_with('botgotsthis', '1', now)

    @patch('source.api.twitch.getTwitchIds')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchId', autospec=True)
    async def test_loadTwitchId_no_id(self, mock_save, mock_now, mock_globals,
                                      mock_getIds):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchId = {}
        mock_globals.twitchIdCache = {}
        mock_getIds.return_value = {}
        self.assertTrue(await utils.loadTwitchId('botgotsthis'))
        mock_now.assert_called_once_with()
        mock_getIds.assert_called_once_with(['botgotsthis'])
        mock_save.assert_called_once_with('botgotsthis', None, now)

    @patch('source.api.twitch.getTwitchIds')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchId', autospec=True)
    async def test_loadTwitchId_api_error(self, mock_save, mock_now,
                                          mock_globals, mock_getIds):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchId = {}
        mock_globals.twitchIdCache = {}
        mock_getIds.return_value = None
        self.assertFalse(await utils.loadTwitchId('botgotsthis'))
        mock_now.assert_called_once_with()
        mock_getIds.assert_called_once_with(['botgotsthis'])
        self.assertFalse(mock_save.called)

    @patch('source.api.twitch.getTwitchIds')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchId', autospec=True)
    async def test_loadTwitchId_timestamp(self, mock_save, mock_now,
                                          mock_globals, mock_getIds):
        now = datetime(2000, 1, 1)
        mock_globals.twitchId = {}
        mock_globals.twitchIdCache = {}
        mock_getIds.return_value = {'botgotsthis': '1'}
        self.assertTrue(await utils.loadTwitchId('botgotsthis', now))
        self.assertFalse(mock_now.called)
        mock_getIds.assert_called_once_with(['botgotsthis'])
        mock_save.assert_called_once_with('botgotsthis', '1', now)

    @patch('source.api.twitch.getTwitchIds')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchId', autospec=True)
    async def test_loadTwitchId_recent(self, mock_save, mock_now, mock_globals,
                                       mock_getIds):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchId = {'botgotsthis': '1'}
        mock_globals.twitchIdCache = {'botgotsthis': now}
        self.assertTrue(await utils.loadTwitchId('botgotsthis'))
        mock_now.assert_called_once_with()
        self.assertFalse(mock_getIds.called)
        self.assertFalse(mock_save.called)

    @patch('source.api.twitch.getTwitchIds')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchId', autospec=True)
    async def test_loadTwitchId_recent_None(self, mock_save, mock_now,
                                            mock_globals, mock_getIds):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchId = {'botgotsthis': None}
        mock_globals.twitchIdCache = {'botgotsthis': now}
        self.assertTrue(await utils.loadTwitchId('botgotsthis'))
        mock_now.assert_called_once_with()
        self.assertFalse(mock_getIds.called)
        self.assertFalse(mock_save.called)

    @patch('source.api.twitch.getTwitchIds')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchId', autospec=True)
    async def test_loadTwitchId_expired(self, mock_save, mock_now,
                                        mock_globals, mock_getIds):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchId = {'botgotsthis': '1'}
        mock_globals.twitchIdCache = {'botgotsthis': now - timedelta(days=1)}
        mock_getIds.return_value = {'botgotsthis': '1'}
        self.assertTrue(await utils.loadTwitchId('botgotsthis'))
        mock_now.assert_called_once_with()
        mock_getIds.assert_called_once_with(['botgotsthis'])
        mock_save.assert_called_once_with('botgotsthis', '1', now)

    @patch('source.api.twitch.getTwitchIds')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchId', autospec=True)
    async def test_loadTwitchId_expired_None(self, mock_save, mock_now,
                                             mock_globals, mock_getIds):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchId = {'botgotsthis': None}
        mock_globals.twitchIdCache = {'botgotsthis': now - timedelta(hours=1)}
        mock_getIds.return_value = {'botgotsthis': '1'}
        self.assertTrue(await utils.loadTwitchId('botgotsthis'))
        mock_now.assert_called_once_with()
        mock_getIds.assert_called_once_with(['botgotsthis'])
        mock_save.assert_called_once_with('botgotsthis', '1', now)

    @patch('source.api.twitch.get_community_by_id')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunityId(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {}
        mock_globals.twitchCommunityId = {}
        mock_globals.twitchCommunityCache = {}
        mock_get.return_value = TwitchCommunity(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421', 'Speedrunning')
        self.assertTrue(await utils.loadTwitchCommunityId(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421'))
        mock_now.assert_called_once_with()
        mock_get.assert_called_once_with(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421')
        mock_save.assert_called_once_with(
            'Speedrunning', '6e940c4a-c42f-47d2-af83-0a2c7e47c421', now)

    @patch('source.api.twitch.get_community_by_id')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunityId_no_match(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {}
        mock_globals.twitchCommunityId = {}
        mock_globals.twitchCommunityCache = {}
        mock_get.return_value = TwitchCommunity(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421', None)
        self.assertTrue(await utils.loadTwitchCommunityId(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421'))
        mock_now.assert_called_once_with()
        mock_get.assert_called_once_with(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421')
        mock_save.assert_called_once_with(
            None, '6e940c4a-c42f-47d2-af83-0a2c7e47c421', now)

    @patch('source.api.twitch.get_community_by_id')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunityId_api_error(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {}
        mock_globals.twitchCommunityId = {}
        mock_globals.twitchCommunityCache = {}
        mock_get.return_value = None
        self.assertFalse(await utils.loadTwitchCommunityId(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421'))
        mock_now.assert_called_once_with()
        mock_get.assert_called_once_with(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421')
        self.assertFalse(mock_save.called)

    @patch('source.api.twitch.get_community_by_id')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunityId_timestamp(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_globals.twitchCommunity = {}
        mock_globals.twitchCommunityId = {}
        mock_globals.twitchCommunityCache = {}
        mock_get.return_value = TwitchCommunity(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421', 'Speedrunning')
        self.assertTrue(await utils.loadTwitchCommunityId(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421', now))
        self.assertFalse(mock_now.called)
        mock_get.assert_called_once_with(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421')
        mock_save.assert_called_once_with(
            'Speedrunning', '6e940c4a-c42f-47d2-af83-0a2c7e47c421', now)

    @patch('source.api.twitch.get_community_by_id')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunityId_recent(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'}
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'speedrunning'}
        mock_globals.twitchCommunityCache = {'speedrunning': now}
        self.assertTrue(await utils.loadTwitchCommunityId(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421'))
        mock_now.assert_called_once_with()
        self.assertFalse(mock_get.called)
        self.assertFalse(mock_save.called)

    @patch('source.api.twitch.get_community_by_id')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunityId_expired(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'}
        mock_globals.twitchCommunityId = {
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421': 'speedrunning'}
        mock_globals.twitchCommunityCache = {
            'speedrunning': now - timedelta(days=1)}
        mock_get.return_value = TwitchCommunity(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421', 'Speedrunning')
        self.assertTrue(await utils.loadTwitchCommunityId(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421'))
        mock_now.assert_called_once_with()
        mock_get.assert_called_once_with(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421')
        mock_save.assert_called_once_with(
            'Speedrunning', '6e940c4a-c42f-47d2-af83-0a2c7e47c421', now)

    @patch('source.api.twitch.get_community_by_id')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunityId_expired_None(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {'speedrunning': None}
        mock_globals.twitchCommunityId = {}
        mock_globals.twitchCommunityCache = {
            'speedrunning': now - timedelta(hours=1)}
        mock_get.return_value = TwitchCommunity(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421', 'Speedrunning')
        self.assertTrue(await utils.loadTwitchCommunityId(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421'))
        mock_now.assert_called_once_with()
        mock_get.assert_called_once_with(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421')
        mock_save.assert_called_once_with(
            'Speedrunning', '6e940c4a-c42f-47d2-af83-0a2c7e47c421', now)

    @patch('source.api.twitch.get_community')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunity(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {}
        mock_globals.twitchCommunityCache = {}
        mock_get.return_value = TwitchCommunity(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421', 'Speedrunning')
        self.assertTrue(await utils.loadTwitchCommunity('Speedrunning'))
        mock_now.assert_called_once_with()
        mock_get.assert_called_once_with('speedrunning')
        mock_save.assert_called_once_with(
            'Speedrunning', '6e940c4a-c42f-47d2-af83-0a2c7e47c421', now)

    @patch('source.api.twitch.get_community')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunity_no_id(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {}
        mock_globals.twitchCommunityCache = {}
        mock_get.return_value = TwitchCommunity(None, None)
        self.assertTrue(await utils.loadTwitchCommunity('Speedrunning'))
        mock_now.assert_called_once_with()
        mock_get.assert_called_once_with('speedrunning')
        mock_save.assert_called_once_with('Speedrunning', None, now)

    @patch('source.api.twitch.get_community')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunity_api_error(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {}
        mock_globals.twitchCommunityCache = {}
        mock_get.return_value = None
        self.assertFalse(await utils.loadTwitchCommunity('Speedrunning'))
        mock_now.assert_called_once_with()
        mock_get.assert_called_once_with('speedrunning')
        self.assertFalse(mock_save.called)

    @patch('source.api.twitch.get_community')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunity_timestamp(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_globals.twitchCommunity = {}
        mock_globals.twitchCommunityCache = {}
        mock_get.return_value = TwitchCommunity(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421', 'Speedrunning')
        self.assertTrue(await utils.loadTwitchCommunity('Speedrunning', now))
        self.assertFalse(mock_now.called)
        mock_get.assert_called_once_with('speedrunning')
        mock_save.assert_called_once_with(
            'Speedrunning', '6e940c4a-c42f-47d2-af83-0a2c7e47c421', now)

    @patch('source.api.twitch.get_community')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunity_recent(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'}
        mock_globals.twitchCommunityCache = {'speedrunning': now}
        self.assertTrue(await utils.loadTwitchCommunity('Speedrunning'))
        mock_now.assert_called_once_with()
        self.assertFalse(mock_get.called)
        self.assertFalse(mock_save.called)

    @patch('source.api.twitch.get_community')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunity_recent_None(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {'speedrunning': None}
        mock_globals.twitchCommunityCache = {'speedrunning': now}
        self.assertTrue(await utils.loadTwitchCommunity('Speedrunning'))
        mock_now.assert_called_once_with()
        self.assertFalse(mock_get.called)
        self.assertFalse(mock_save.called)

    @patch('source.api.twitch.get_community')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunity_expired(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421'}
        mock_globals.twitchCommunityCache = {
            'speedrunning': now - timedelta(days=1)}
        mock_get.return_value = TwitchCommunity(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421', 'Speedrunning')
        self.assertTrue(await utils.loadTwitchCommunity('Speedrunning'))
        mock_now.assert_called_once_with()
        mock_get.assert_called_once_with('speedrunning')
        mock_save.assert_called_once_with(
            'Speedrunning', '6e940c4a-c42f-47d2-af83-0a2c7e47c421', now)

    @patch('source.api.twitch.get_community')
    @patch('bot.globals', autospec=True)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.utils.saveTwitchCommunity', autospec=True)
    async def test_loadTwitchCommunity_expired_None(
            self, mock_save, mock_now, mock_globals, mock_get):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_globals.twitchCommunity = {'speedrunning': None}
        mock_globals.twitchCommunityCache = {
            'speedrunning': now - timedelta(hours=1)}
        mock_get.return_value = TwitchCommunity(
            '6e940c4a-c42f-47d2-af83-0a2c7e47c421', 'Speedrunning')
        self.assertTrue(await utils.loadTwitchCommunity('Speedrunning'))
        mock_now.assert_called_once_with()
        mock_get.assert_called_once_with('speedrunning')
        mock_save.assert_called_once_with(
            'Speedrunning', '6e940c4a-c42f-47d2-af83-0a2c7e47c421', now)


class TesEnsureServer(unittest.TestCase):
    def setUp(self):
        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.clusters = {
            'justin': Mock(spec=connection.ConnectionHandler),
            'twitch': Mock(spec=connection.ConnectionHandler)
            }
        self.channel = Mock(spec=Channel)
        self.mock_globals.channels = {
            'botgotsthis': self.channel
            }
        self.channel.socket = self.mock_globals.clusters['justin']
        self.channel.joinPriority = 0

    @patch('bot.utils.joinChannel', autospec=True)
    @patch('bot.utils.partChannel', autospec=True)
    def test(self, mock_part, mock_join):
        self.assertEqual(utils.ensureServer('botgotsthis', cluster='twitch'),
                         utils.ENSURE_REJOIN)
        mock_part.assert_called_once_with('botgotsthis')
        mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')

    @patch('bot.utils.joinChannel', autospec=True)
    @patch('bot.utils.partChannel', autospec=True)
    def test_priority(self, mock_part, mock_join):
        self.assertEqual(
            utils.ensureServer('botgotsthis', -1, cluster='twitch'),
            utils.ENSURE_REJOIN)
        mock_part.assert_called_once_with('botgotsthis')
        mock_join.assert_called_once_with('botgotsthis', -1, 'twitch')

    @patch('bot.utils.joinChannel', autospec=True)
    @patch('bot.utils.partChannel', autospec=True)
    def test_correct(self, mock_part, mock_join):
        self.assertEqual(utils.ensureServer('botgotsthis', cluster='justin'),
                          utils.ENSURE_CORRECT)

    @patch('bot.utils.joinChannel', autospec=True)
    @patch('bot.utils.partChannel', autospec=True)
    def test_correct_priority(self, mock_part, mock_join):
        self.assertEqual(
            utils.ensureServer('botgotsthis', -1, cluster='justin'),
            utils.ENSURE_CORRECT)
        self.assertEqual(self.channel.joinPriority, -1)

    def test_None(self):
        self.assertRaises(TypeError, utils.ensureServer, None)

    def test_server_None(self):
        self.assertRaises(TypeError,
                          utils.ensureServer, 'botgotsthis', cluster=None)

    @patch('bot.utils.partChannel', autospec=True)
    def test_server_not_in(self, mock_part):
        self.assertEqual(
            utils.ensureServer('botgotsthis', cluster=''),
            utils.ENSURE_CLUSTER_UNKNOWN)
        mock_part.assert_called_once_with('botgotsthis')
