from datetime import timedelta
from unittest.mock import patch

from source.public.channel import broadcaster
from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import StrContains


class TestChannelBroadcaster(TestChannel):
    def test_hello(self):
        self.assertIs(broadcaster.commandHello(self.args), False)
        self.permissionSet['broadcaster'] = True
        self.assertIs(broadcaster.commandHello(self.args), True)
        self.channel.send.assert_called_once_with(StrContains('Hello', '!'))

    @patch('source.public.library.broadcaster.come', autospec=True)
    def test_come(self, mock_come):
        self.assertIs(broadcaster.commandCome(self.args), False)
        self.assertFalse(mock_come.called)
        mock_come.return_value = True
        self.permissions.inOwnerChannel = True
        self.assertIs(broadcaster.commandCome(self.args), True)
        mock_come.assert_called_once_with(self.database, 'botgotsthis',
                                          self.channel.send)

    @patch('source.public.library.broadcaster.leave', autospec=True)
    def test_leave(self, mock_leave):
        self.assertIs(broadcaster.commandLeave(self.args), False)
        self.assertFalse(mock_leave.called)
        mock_leave.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(broadcaster.commandLeave(self.args), True)
        mock_leave.assert_called_once_with('botgotsthis', self.channel.send)

    @patch('source.public.library.broadcaster.empty', autospec=True)
    def test_empty(self, mock_empty):
        self.assertIs(broadcaster.commandEmpty(self.args), False)
        self.assertFalse(mock_empty.called)
        mock_empty.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(broadcaster.commandEmpty(self.args), True)
        mock_empty.assert_called_once_with('botgotsthis', self.channel.send)

    @patch('source.public.library.broadcaster.auto_join', autospec=True)
    def test_auto_join(self, mock_autojoin):
        self.assertIs(broadcaster.commandAutoJoin(self.args), False)
        self.assertFalse(mock_autojoin.called)
        mock_autojoin.return_value = True
        self.permissions.inOwnerChannel = True
        self.assertIs(broadcaster.commandAutoJoin(self.args), True)
        mock_autojoin.assert_called_once_with(
            self.database, 'botgotsthis', self.channel.send, self.args.message)

    @patch('source.public.library.broadcaster.set_timeout_level',
           autospec=True)
    def test_set_timeout_level(self, mock_set_timeout):
        self.assertIs(broadcaster.commandSetTimeoutLevel(self.args), False)
        self.assertFalse(mock_set_timeout.called)
        mock_set_timeout.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(broadcaster.commandSetTimeoutLevel(self.args), True)
        mock_set_timeout.assert_called_once_with(
            self.database, 'botgotsthis', self.channel.send, self.args.message)

    @patch('source.api.twitch.server_time', autospec=True)
    def test_uptime(self, mock_server_time):
        self.channel.isStreaming = False
        self.assertIs(broadcaster.commandUptime(self.args), True)
        self.assertFalse(mock_server_time.called)
        self.channel.send.assert_called_once_with(
            StrContains('botgotsthis', 'not', 'streaming'))

    @patch('source.api.twitch.server_time', autospec=True)
    def test_uptime_isstreaming(self, mock_server_time):
        self.channel.isStreaming = True
        self.channel.streamingSince = self.now
        mock_server_time.return_value = self.now
        self.assertIs(broadcaster.commandUptime(self.args), True)
        mock_server_time.assert_called_once_with()
        self.channel.send.assert_called_once_with(
            StrContains('Uptime', str(timedelta())))

    @patch('source.api.twitch.server_time', autospec=True)
    def test_uptime_server_error(self, mock_server_time):
        self.channel.isStreaming = True
        mock_server_time.return_value = None
        self.assertIs(broadcaster.commandUptime(self.args), True)
        mock_server_time.assert_called_once_with()
        self.channel.send.assert_called_once_with(
            StrContains('Failed', 'twitch.tv'))
