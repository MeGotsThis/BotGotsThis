import unittest
from bot import utils
from bot.data import Channel, Socket, MessagingQueue
from bot.thread.logging import Logging
from datetime import datetime
from io import StringIO
from tests.unittest.mock_class import StrContains
from unittest.mock import Mock, patch


class TestUtils(unittest.TestCase):
    def test_now(self):
        self.assertIsInstance(utils.now(), datetime)

    @patch('bot.globals', autospec=True)
    def test_joinChannel_none(self, mock_globals):
        mock_globals.channels = {}
        mock_globals.clusters = {
            'aws': Mock(spec=Socket)
            }
        self.assertRaises(TypeError, utils.joinChannel, None)

    @patch('bot.globals', autospec=True)
    def test_joinChannel_nocluster(self, mock_globals):
        mock_globals.channels = {}
        mock_globals.clusters = {
            'twitch': Mock(spec=Socket)
            }
        self.assertIs(
            utils.joinChannel('botgotsthis', cluster='botgotsthis'), None)
        self.assertNotIn('botgotsthis', mock_globals.channels)

    @patch('bot.globals', autospec=True)
    def test_joinChannel_existing_channel(self, mock_globals):
        mock_globals.clusters = {
            'twitch': Mock(spec=Socket)
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
            'twitch': Mock(spec=Socket)
            }
        self.assertIs(utils.joinChannel('botgotsthis', 0, 'twitch'), True)
        self.assertIn('botgotsthis', mock_globals.channels)
        self.assertEqual(mock_globals.channels['botgotsthis'].joinPriority, 0)
        mock_globals.clusters['twitch'].joinChannel.assert_called_once_with(
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
        socket = Mock(spec=Socket)
        socket.messaging = Mock(spec=MessagingQueue)
        mock_globals.clusters = {
            'twitch': socket
            }
        mock_globals.whisperCluster = 'twitch'
        utils.whisper('botgotsthis', 'Kappa')
        socket.messaging.sendWhisper.assert_called_once_with(
            'botgotsthis', 'Kappa')

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
    def test_print_override(self, mock_now, mock_config, mock_stdout):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.development = True
        utils.print('Kappa', override=True)
        self.assertEqual(mock_stdout.getvalue(), '2000-01-01 00:00:00 Kappa\n')

    @patch('bot.globals', autospec=True)
    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_print_file(self, mock_now, mock_config, mock_stdout,
                        mock_globals):
        mock_globals.logging = Mock(spec=Logging)
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.development = False
        utils.print('Kappa', file=True)
        self.assertEqual(mock_stdout.getvalue(), '')
        mock_globals.logging.log.assert_called_once_with(
            'output.log', '2000-01-01T00:00:00.000000 Kappa\n')

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_logIrcMessage_config(self, mock_now, mock_config, mock_globals):
        mock_globals.logging = Mock(spec=Logging)
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.ircLogFolder = 'log'
        utils.logIrcMessage('botgotsthis', 'Kappa')
        mock_globals.logging.log.assert_called_once_with(
            StrContains('botgotsthis'), StrContains('Kappa'))

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_logIrcMessage_config_None(self, mock_now, mock_config,
                                       mock_globals):
        mock_globals.logging = Mock(spec=Logging)
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.ircLogFolder = None
        utils.logIrcMessage('botgotsthis', 'Kappa')
        self.assertFalse(mock_globals.logging.log.called)

    @patch('sys.stderr', new_callable=StringIO)
    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_logException(self, mock_now, mock_config, mock_globals,
                          mock_stderr):
        mock_globals.logging = Mock(spec=Logging)
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.development = True
        mock_config.exceptionLog = 'exception'
        try:
            raise Exception()
        except Exception:
            utils.logException()
        mock_globals.logging.log.assert_called_once_with(
            StrContains('exception'),
            StrContains('2000', '01', 'Exception', __file__,
                        'test_logException', 'raise Exception'))
        self.assertEquals(mock_stderr.getvalue(),
                          StrContains('2000', '1', 'Exception', __file__,
                                      'test_logException', 'raise Exception'))

    @patch('sys.stderr', new_callable=StringIO)
    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_logException_no_development(
            self, mock_now, mock_config, mock_globals, mock_stderr):
        mock_globals.logging = Mock(spec=Logging)
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.development = False
        mock_config.exceptionLog = 'exception'
        try:
            raise Exception()
        except Exception:
            utils.logException()
        mock_globals.logging.log.assert_called_once_with(
            StrContains('exception'),
            StrContains('2000', '1', 'Exception', __file__,
                        'test_logException', 'raise Exception'))
        self.assertEquals(mock_stderr.getvalue(), '')

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_logException_config_None(self, mock_now, mock_config,
                                      mock_globals):
        mock_globals.logging = Mock(spec=Logging)
        mock_now.return_value = datetime(2000, 1, 1)
        mock_config.exceptionLog = None
        try:
            raise Exception()
        except Exception:
            utils.logException()
        self.assertFalse(mock_globals.logging.log.called)


class TesEnsureServer(unittest.TestCase):
    def setUp(self):
        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.clusters = {
            'justin': Mock(spec=Socket),
            'twitch': Mock(spec=Socket)
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
