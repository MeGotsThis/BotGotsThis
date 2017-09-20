from asynctest.mock import patch

from tests.unittest.base_managebot import TestManageBot
from tests.unittest.mock_class import StrContains

# Needs to be imported last
from pkg.botgotsthis.manage import listchats


class TestManageBotListChats(TestManageBot):
    @patch('source.helper.message.messagesFromItems', autospec=True)
    @patch('bot.globals', autospec=True)
    async def test_no_channels(self, mock_globals, mock_messages):
        mock_globals.channels = ''
        self.assertIs(await listchats.manageListChats(self.args), True)
        self.assertFalse(mock_messages.called)
        self.send.assert_called_once_with(StrContains('not', 'in'))

    @patch('source.helper.message.messagesFromItems', autospec=True)
    @patch('bot.globals', autospec=True)
    async def test_one_channel(self, mock_globals, mock_messages):
        mock_globals.channels = {'botgotsthis': None}
        mock_messages.return_value = ''
        self.assertIs(await listchats.manageListChats(self.args), True)
        mock_messages.assert_called_once_with(['botgotsthis'],
                                              StrContains('Chats'))
        self.send.assert_called_once_with('')

    @patch('source.helper.message.messagesFromItems', autospec=True)
    @patch('bot.globals', autospec=True)
    async def test_many_channel(self, mock_globals, mock_messages):
        mock_globals.channels = {'botgotsthis': None,
                                 'mebotsthis': None,
                                 'megotsthis': None}
        mock_messages.return_value = ''
        self.assertIs(await listchats.manageListChats(self.args), True)
        mock_messages.assert_called_once_with(
            ['botgotsthis', 'mebotsthis', 'megotsthis'], StrContains('Chats'))
        self.send.assert_called_once_with('')
