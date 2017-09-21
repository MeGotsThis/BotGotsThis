import unittest

import asynctest

from datetime import datetime

from asynctest.mock import CoroutineMock, MagicMock, Mock, PropertyMock
from asynctest.mock import call, patch

from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from lib import channel
from lib.database import DatabaseMain
from lib.data.message import Message


class TestChannel(asynctest.TestCase):
    def setUp(self):
        self.tags = IrcMessageTags(IrcMessageTags.parseTags(
            'display-name=BotGotsThis;id=0;subscriber=0;turbo=0;mod=1;'
            'user-type=mod;badges=broadcaster/1;color=#FFFFFF;emotes=;'
            'room-id=2;user-id=1'))
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'megotsthis'
        self.now = datetime(2000, 1, 1)

    @patch('lib.channel.chatCommand')
    async def test_parse(self, mock_chatCommand):
        channel.parse(self.channel, self.tags, 'botgotsthis', 'Kappa',
                      self.now)
        self.assertTrue(mock_chatCommand.called)

    @asynctest.fail_on(unused_loop=False)
    @patch('lib.channel.chatCommand')
    def test_parse_empty(self, mock_chatCommand):
        channel.parse(self.channel, self.tags, 'botgotsthis', '', self.now)
        self.assertFalse(mock_chatCommand.called)

    @asynctest.fail_on(unused_loop=False)
    @patch('lib.channel.chatCommand')
    def test_parse_spaces(self, mock_chatCommand):
        channel.parse(self.channel, self.tags, 'botgotsthis', '  ', self.now)
        self.assertFalse(mock_chatCommand.called)

    @patch('bot.utils.logException', autospec=True)
    @patch('bot.utils.saveTwitchId', autospec=True)
    @patch('lib.database.get_database')
    @patch('lib.channel.commandsToProcess', autospec=True)
    async def test_chatCommand(self, mock_commands, mock_database, mock_save,
                               mock_log):
        command1 = CoroutineMock(spec=lambda args: False, return_value=False)
        command2 = CoroutineMock(spec=lambda args: False, return_value=True)
        command3 = CoroutineMock(spec=lambda args: False, return_value=False)
        mock_commands.return_value = [command1, command2, command3]
        database = MagicMock(spec=DatabaseMain)
        database.__aenter__.return_value = database
        database.isPermittedUser.return_value = False
        database.isBotManager.return_value = False
        database.__aexit__.return_value = True
        mock_database.return_value = database
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        await channel.chatCommand(self.channel, self.tags, 'botgotsthis',
                                  message, self.now)
        mock_save.assert_has_calls([call('megotsthis', '2', self.now),
                                    call('botgotsthis', '1', self.now)])
        self.assertEqual(database.isPermittedUser.call_count, 1)
        self.assertEqual(database.isBotManager.call_count, 1)
        self.assertEqual(mock_commands.call_count, 1)
        self.assertEqual(command1.call_count, 1)
        self.assertEqual(command2.call_count, 1)
        self.assertEqual(command3.call_count, 0)
        self.assertEqual(mock_log.call_count, 0)

    @patch('bot.utils.logException', autospec=True)
    @patch('lib.database.get_database')
    @patch('lib.channel.commandsToProcess', autospec=True)
    async def test_chatCommand_except(self, mock_commands, mock_database,
                                      mock_log):
        command = CoroutineMock(spec=lambda args: False, side_effect=Exception)
        mock_commands.return_value = [command, command]
        database = MagicMock(spec=DatabaseMain)
        database.__aenter__.return_value = database
        database.isPermittedUser.return_value = False
        database.isBotManager.return_value = False
        database.__aexit__.return_value = False
        mock_database.return_value = database
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        await channel.chatCommand(self.channel, self.tags, 'botgotsthis',
                                  message, self.now)
        self.assertEqual(database.isPermittedUser.call_count, 1)
        self.assertEqual(database.isBotManager.call_count, 1)
        self.assertEqual(mock_commands.call_count, 1)
        self.assertEqual(command.call_count, 1)
        self.assertTrue(mock_log.called)

    @patch('bot.utils.logException', autospec=True)
    @patch('lib.database.get_database')
    @patch('lib.channel.commandsToProcess', autospec=True)
    async def test_chatCommand_database_except(self, mock_commands,
                                               mock_database, mock_log):
        mock_database.side_effect = Exception
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        await channel.chatCommand(self.channel, self.tags, 'botgotsthis',
                                  message, self.now)
        self.assertFalse(mock_commands.called)
        self.assertTrue(mock_log.called)

    @patch('bot.utils.logException', autospec=True)
    @patch('bot.utils.saveTwitchId', autospec=True)
    @patch('lib.database.get_database')
    @patch('lib.channel.commandsToProcess', autospec=True)
    async def test_chatCommand_no_tags(self, mock_commands, mock_database,
                                       mock_save, mock_log):
        command1 = CoroutineMock(spec=lambda args: False, return_value=False)
        command2 = CoroutineMock(spec=lambda args: False, return_value=True)
        command3 = CoroutineMock(spec=lambda args: False, return_value=False)
        mock_commands.return_value = [command1, command2, command3]
        database = MagicMock(spec=DatabaseMain)
        database.__aenter__.return_value = database
        database.isPermittedUser.return_value = False
        database.isBotManager.return_value = False
        database.__aexit__.return_value = True
        mock_database.return_value = database
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        await channel.chatCommand(self.channel, None, 'botgotsthis', message,
                                  self.now)
        self.assertFalse(mock_save.called)
        self.assertEqual(database.isPermittedUser.call_count, 1)
        self.assertEqual(database.isBotManager.call_count, 1)
        self.assertEqual(mock_commands.call_count, 1)
        self.assertEqual(command1.call_count, 1)
        self.assertEqual(command2.call_count, 1)
        self.assertEqual(command3.call_count, 0)
        self.assertEqual(mock_log.call_count, 0)


class TestChannelCommandToProcess(unittest.TestCase):
    def setUp(self):
        patcher = patch('lists.channel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_list = patcher.start()
        self.mock_list.filterMessage.return_value = []
        self.mock_list.commands.return_value = {}
        self.mock_list.commandsStartWith.return_value = {}
        self.mock_list.processNoCommand.return_value = []

        self.command1 = lambda args: False
        self.command2 = lambda args: False
        self.command3 = lambda args: False
        self.command4 = lambda args: False

    def test_commandsToProcess_empty(self):
        self.assertEqual(list(channel.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_specific(self):
        self.mock_list.commands.return_value['!kappa'] = self.command1
        self.assertEqual(
            list(channel.commandsToProcess('!kappa')), [self.command1])

    def test_commandsToProcess_specific_no_match(self):
        self.mock_list.commands.return_value['!kappahd'] = self.command1
        self.assertEqual(list(channel.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_specific_none(self):
        self.mock_list.commands.return_value['!kappa'] = None
        self.assertEqual(list(channel.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_startswith(self):
        self.mock_list.commandsStartWith.return_value['!k'] = self.command1
        self.assertEqual(
            list(channel.commandsToProcess('!kappa')), [self.command1])

    def test_commandsToProcess_startswith_exact(self):
        self.mock_list.commandsStartWith.return_value['!kappa'] = self.command1
        self.assertEqual(
            list(channel.commandsToProcess('!kappa')), [self.command1])

    def test_commandsToProcess_startswith_none(self):
        self.mock_list.commandsStartWith.return_value['!k'] = None
        self.assertEqual(list(channel.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_startswith_no_match(self):
        commands = self.mock_list.commandsStartWith.return_value
        commands['!kevinturtle'] = self.command1
        self.assertEqual(list(channel.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_startswith_multiple(self):
        self.mock_list.commandsStartWith.return_value['!k'] = self.command1
        self.mock_list.commandsStartWith.return_value['!ka'] = self.command2
        self.assertCountEqual(
            list(channel.commandsToProcess('!kappa')),
            [self.command1, self.command2])

    def test_commandsToProcess_specific_startswith(self):
        self.mock_list.commands.return_value['!kappa'] = self.command1
        self.mock_list.commandsStartWith.return_value['!k'] = self.command2
        self.mock_list.commandsStartWith.return_value['!ka'] = self.command3
        self.assertCountEqual(
            list(channel.commandsToProcess('!kappa')),
            [self.command1, self.command2, self.command3])

    def test_commandsToProcess_filter(self):
        self.mock_list.filterMessage.return_value.append(self.command1)
        self.assertCountEqual(
            list(channel.commandsToProcess('')), [self.command1])

    def test_commandsToProcess_nocommand(self):
        self.mock_list.processNoCommand.return_value.append(self.command1)
        self.assertCountEqual(
            list(channel.commandsToProcess('')), [self.command1])

    def test_commandsToProcess_ordering(self):
        self.mock_list.filterMessage.return_value.append(self.command1)
        self.mock_list.commands.return_value['!kappa'] = self.command2
        self.mock_list.commandsStartWith.return_value['!k'] = self.command3
        self.mock_list.processNoCommand.return_value.append(self.command4)
        self.assertCountEqual(
            list(channel.commandsToProcess('!kappa')),
            [self.command1, self.command2, self.command3, self.command4])
