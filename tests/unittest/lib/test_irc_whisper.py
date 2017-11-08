import unittest

import asynctest

from datetime import datetime

from asynctest.mock import CoroutineMock, MagicMock, Mock, PropertyMock, patch

from bot.twitchmessage import IrcMessageTags
from lib import whisper
from lib.cache import CacheStore
from lib.data.message import Message


class TestWhisper(asynctest.TestCase):
    def setUp(self):
        self.tags = IrcMessageTags(IrcMessageTags.parseTags(
            'turbo=1;display-name=BotGotsThis;badges=;emotes=;user-id=1;'
            'message-id=1;thread-id=1;user-type=;color=#FFFFFF'))
        self.now = datetime(2000, 1, 1)

    @patch('lib.whisper.whisperCommand')
    async def test_parse(self, mock_whisperCommand):
        whisper.parse(self.tags, 'botgotsthis', 'Kappa', self.now)
        self.assertTrue(mock_whisperCommand.called)

    @asynctest.fail_on(unused_loop=False)
    @patch('lib.whisper.whisperCommand')
    def test_parse_empty(self, mock_whisperCommand):
        whisper.parse(self.tags, 'botgotsthis', '', self.now)
        self.assertFalse(mock_whisperCommand.called)

    @asynctest.fail_on(unused_loop=False)
    @patch('lib.whisper.whisperCommand')
    def test_parse_spaces(self, mock_whisperCommand):
        whisper.parse(self.tags, 'botgotsthis', '  ', self.now)
        self.assertFalse(mock_whisperCommand.called)

    @patch('lib.cache.get_cache')
    @patch('lib.whisper.commandsToProcess', autospec=True)
    async def test_whisperCommand(self, mock_commands, mock_data):
        command1 = CoroutineMock(spec=lambda args: False, return_value=False)
        command2 = CoroutineMock(spec=lambda args: False, return_value=True)
        command3 = CoroutineMock(spec=lambda args: False, return_value=False)
        mock_commands.return_value = [command1, command2, command3]
        data = MagicMock(spec=CacheStore)
        data.__aenter__.return_value = data
        data.__aexit__.return_value = True
        mock_data.return_value = data
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        await whisper.whisperCommand(self.tags, 'botgotsthis', message,
                                     self.now)
        self.assertEqual(data.isBotManager.call_count, 1)
        self.assertEqual(mock_commands.call_count, 1)
        self.assertEqual(command1.call_count, 1)
        self.assertEqual(command2.call_count, 1)
        self.assertEqual(command3.call_count, 0)

    @patch('bot.utils.logException', autospec=True)
    @patch('lib.cache.get_cache')
    @patch('lib.whisper.commandsToProcess', autospec=True)
    async def test_whisperCommand_except(self, mock_commands, mock_data,
                                         mock_log):
        command = CoroutineMock(spec=lambda args: False, side_effect=Exception)
        mock_commands.return_value = [command, command]
        data = MagicMock(spec=CacheStore)
        data.__aenter__.return_value = data
        data.__aexit__.return_value = False
        mock_data.return_value = data
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        await whisper.whisperCommand(self.tags, 'botgotsthis', message,
                                     self.now)
        self.assertEqual(data.isBotManager.call_count, 1)
        self.assertEqual(mock_commands.call_count, 1)
        self.assertEqual(command.call_count, 1)
        self.assertTrue(mock_log.called)

    @patch('bot.utils.logException', autospec=True)
    @patch('lib.cache.get_cache')
    @patch('lib.whisper.commandsToProcess', autospec=True)
    async def test_whisperCommand_data_except(
            self, mock_commands, mock_data, mock_log):
        mock_data.side_effect = Exception
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        await whisper.whisperCommand(self.tags, 'botgotsthis', message,
                                     self.now)
        self.assertFalse(mock_commands.called)
        self.assertTrue(mock_log.called)


class TestWhisperCommandToProcess(unittest.TestCase):
    def setUp(self):
        patcher = patch('lib.items.whisper', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_list = patcher.start()
        self.mock_list.commands.return_value = {}
        self.mock_list.commandsStartWith.return_value = {}

        self.command1 = lambda args: False
        self.command2 = lambda args: False
        self.command3 = lambda args: False

    def test_commandsToProcess_empty(self):
        self.assertEqual(list(whisper.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_specific(self):
        self.mock_list.commands.return_value['!kappa'] = self.command1
        self.assertEqual(
            list(whisper.commandsToProcess('!kappa')), [self.command1])

    def test_commandsToProcess_specific_no_match(self):
        self.mock_list.commands.return_value['!kappahd'] = self.command1
        self.assertEqual(list(whisper.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_specific_none(self):
        self.mock_list.commands.return_value['!kappa'] = None
        self.assertEqual(list(whisper.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_startswith(self):
        self.mock_list.commandsStartWith.return_value['!k'] = self.command1
        self.assertEqual(
            list(whisper.commandsToProcess('!kappa')), [self.command1])

    def test_commandsToProcess_startswith_exact(self):
        self.mock_list.commandsStartWith.return_value['!kappa'] = self.command1
        self.assertEqual(
            list(whisper.commandsToProcess('!kappa')), [self.command1])

    def test_commandsToProcess_startswith_none(self):
        self.mock_list.commandsStartWith.return_value['!k'] = None
        self.assertEqual(list(whisper.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_startswith_no_match(self):
        commands = self.mock_list.commandsStartWith.return_value
        commands['!kevinturtle'] = self.command1
        self.assertEqual(list(whisper.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_startswith_multiple(self):
        self.mock_list.commandsStartWith.return_value['!k'] = self.command1
        self.mock_list.commandsStartWith.return_value['!ka'] = self.command2
        self.assertCountEqual(
            list(whisper.commandsToProcess('!kappa')),
            [self.command1, self.command2])

    def test_commandsToProcess_specific_startswith(self):
        self.mock_list.commands.return_value['!kappa'] = self.command1
        self.mock_list.commandsStartWith.return_value['!k'] = self.command2
        self.mock_list.commandsStartWith.return_value['!ka'] = self.command3
        self.assertCountEqual(
            list(whisper.commandsToProcess('!kappa')),
            [self.command1, self.command2, self.command3])
