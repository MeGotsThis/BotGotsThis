import unittest

from datetime import datetime
from io import StringIO
from asynctest.mock import Mock, patch

from bot import utils
from bot.coroutine import connection
from bot.data import Channel, MessagingQueue
from tests.unittest.mock_class import StrContains


class TestUtils(unittest.TestCase):
    def test_now(self):
        self.assertIsInstance(utils.now(), datetime)

    @patch('bot.globals', autospec=True)
    def test_joinChannel_none(self, mock_globals):
        mock_globals.channels = {}
        mock_globals.cluster = Mock(spec=connection.ConnectionHandler)
        self.assertRaises(TypeError, utils.joinChannel, None)

    @patch('bot.globals', autospec=True)
    def test_joinChannel_existing_channel(self, mock_globals):
        mock_globals.cluster = Mock(spec=connection.ConnectionHandler)
        mock_globals.channels = {
            'botgotsthis': Channel('botgotsthis', mock_globals.cluster, 1)
            }
        self.assertIs(
            utils.joinChannel('botgotsthis', 0), False)
        self.assertIn('botgotsthis', mock_globals.channels)
        self.assertEqual(mock_globals.channels['botgotsthis'].joinPriority, 0)

    @patch('bot.globals', autospec=True)
    def test_joinChannel(self, mock_globals):
        mock_globals.channels = {}
        mock_globals.cluster = Mock(spec=connection.ConnectionHandler)
        self.assertIs(utils.joinChannel('botgotsthis', 0), True)
        self.assertIn('botgotsthis', mock_globals.channels)
        self.assertEqual(mock_globals.channels['botgotsthis'].joinPriority, 0)
        mock_globals.cluster.join_channel.assert_called_once_with(
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
        mock_globals.cluster = connection_
        utils.whisper('botgotsthis', 'Kappa')
        connection_.messaging.sendWhisper.assert_called_once_with(
            'botgotsthis', 'Kappa')

    @patch('bot.globals', autospec=True)
    def test_clearAllChat(self, mock_globals):
        connection_ = Mock(spec=connection.ConnectionHandler)
        connection_.messaging = Mock(spec=MessagingQueue)
        mock_globals.cluster = connection_
        utils.clearAllChat()
        connection_.messaging.clearAllChat.assert_called_once_with()

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

    def test_property_bool_None(self):
        self.assertIsNone(utils.property_bool(None))

    def test_property_bool_True(self):
        pValue = utils.property_bool(True)
        self.assertIsNotNone(pValue)
        self.assertTrue(pValue)

    def test_property_bool_False(self):
        pValue = utils.property_bool(False)
        self.assertIsNotNone(pValue)
        self.assertFalse(pValue)

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
