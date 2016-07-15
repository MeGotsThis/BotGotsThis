import unittest
from bot.twitchmessage import IrcMessageTags
from datetime import datetime
from source import whisper
from source.data import Message
from source.database import DatabaseBase
from unittest.mock import MagicMock, Mock, PropertyMock, patch


class TestWhisper(unittest.TestCase):
    def setUp(self):
        self.tags = IrcMessageTags(IrcMessageTags.parseTags(
            'turbo=1;display-name=BotGotsThis;badges=;emotes=;user-id=1;'
            'message-id=1;thread-id=1;user-type=;color=#FFFFFF'))
        self.now = datetime(2000, 1, 1)

    @patch('source.whisper.whisperCommand', autospec=True)
    def test_parse(self, mock_whisperCommand):
        whisper.parse(self.tags, 'botgotsthis', 'Kappa', self.now)
        self.assertTrue(mock_whisperCommand.called)

    @patch('source.whisper.whisperCommand', autospec=True)
    def test_parse_empty(self, mock_whisperCommand):
        whisper.parse(self.tags, 'botgotsthis', '', self.now)
        self.assertFalse(mock_whisperCommand.called)

    @patch('source.whisper.whisperCommand', autospec=True)
    def test_parse_spaces(self, mock_whisperCommand):
        whisper.parse(self.tags, 'botgotsthis', '  ', self.now)
        self.assertFalse(mock_whisperCommand.called)

    @patch('source.whisper.getDatabase', autospec=True)
    @patch('source.whisper.commandsToProcess', autospec=True)
    def test_whisperCommand(self, mock_commands, mock_database):
        command1 = Mock(spec=lambda args: False, return_value=False)
        command2 = Mock(spec=lambda args: False, return_value = True)
        command3 = Mock(spec=lambda args: False, return_value = False)
        mock_commands.return_value = [command1, command2, command3]
        database = MagicMock(spec=DatabaseBase)
        database.__exit__.return_value = True
        mock_database.return_value = database
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        whisper.whisperCommand(self.tags, 'botgotsthis', message, self.now)
        self.assertEqual(mock_commands.call_count, 1)
        self.assertEqual(command1.call_count, 1)
        self.assertEqual(command2.call_count, 1)
        self.assertEqual(command3.call_count, 0)

    @patch('source.whisper.utils.logException', autospec=True)
    @patch('source.whisper.getDatabase', autospec=True)
    @patch('source.whisper.commandsToProcess', autospec=True)
    def test_whisperCommand_except(self, mock_commands, mock_database, mock_log):
        command = Mock(spec=lambda args: False, side_effect=Exception)
        mock_commands.return_value = [command, command]
        database = MagicMock(spec=DatabaseBase)
        database.__exit__.return_value = False
        mock_database.return_value = database
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        whisper.whisperCommand(self.tags, 'botgotsthis', message, self.now)
        self.assertEqual(mock_commands.call_count, 1)
        self.assertEqual(command.call_count, 1)
        self.assertTrue(mock_log.called)

    @patch('source.whisper.utils.logException', autospec=True)
    @patch('source.whisper.getDatabase', autospec=True)
    @patch('source.whisper.commandsToProcess', autospec=True)
    def test_whisperCommand_database_except(self, mock_commands, mock_database, mock_log):
        mock_database.side_effect = Exception
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        whisper.whisperCommand(self.tags, 'botgotsthis', message, self.now)
        self.assertFalse(mock_commands.called)
        self.assertTrue(mock_log.called)


class TestWhisperCommandToProcess(unittest.TestCase):
    def setUp(self):
        patcher = patch('source.whisper.lists.whisper', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_list = patcher.start()
        self.mock_list.commands = {}

        self.command = lambda args: False

    def test_commandsToProcess_empty(self):
        self.assertEqual(list(whisper.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_specific(self):
        self.mock_list.commands['!kappa'] = self.command
        self.assertEqual(
            list(whisper.commandsToProcess('!kappa')), [self.command])

    def test_commandsToProcess_specific_no_match(self):
        self.mock_list.commands['!kappahd'] = self.command
        self.assertEqual(list(whisper.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_specific_none(self):
        self.mock_list.commands['!kappa'] = None
        self.assertEqual(list(whisper.commandsToProcess('!kappa')), [])
