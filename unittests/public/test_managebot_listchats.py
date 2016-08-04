from source.public.manage import listchats
from unittest.mock import ANY, patch
from unittests.public.test_managebot import TestManageBot


class TestManageBotListChats(TestManageBot):
    @patch('source.public.library.message.messagesFromItems', autospec=True)
    @patch('bot.globals', autospec=True)
    def test_no_channels(self, mock_globals, mock_messages):
        mock_globals.channels = {}
        self.assertIs(listchats.manageListChats(self.args), True)
        self.assertFalse(mock_messages.called)
        self.send.assert_called_once_with(ANY)

    @patch('source.public.library.message.messagesFromItems', autospec=True)
    @patch('bot.globals', autospec=True)
    def test_one_channel(self, mock_globals, mock_messages):
        mock_globals.channels = {'botgotsthis': None}
        mock_messages.return_value = []
        self.assertIs(listchats.manageListChats(self.args), True)
        mock_messages.assert_called_once_with(['botgotsthis'], ANY)
        self.send.assert_called_once_with(ANY)

    @patch('source.public.library.message.messagesFromItems', autospec=True)
    @patch('bot.globals', autospec=True)
    def test_many_channel(self, mock_globals, mock_messages):
        mock_globals.channels = {'botgotsthis': None,
                                 'mebotsthis': None,
                                 'megotsthis': None}
        mock_messages.return_value = []
        self.assertIs(listchats.manageListChats(self.args), True)
        mock_messages.assert_called_once_with(
            ['botgotsthis', 'mebotsthis', 'megotsthis'], ANY)
        self.send.assert_called_once_with(ANY)
