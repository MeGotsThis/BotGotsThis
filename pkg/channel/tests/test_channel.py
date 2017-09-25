from asynctest.mock import patch

from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import StrContains

# Needs to be imported last
from .. import channel


class TestChannelBroadcaster(TestChannel):
    async def test_hello(self):
        self.assertIs(await channel.commandHello(self.args), False)
        self.permissionSet['broadcaster'] = True
        self.assertIs(await channel.commandHello(self.args), True)
        self.channel.send.assert_called_once_with(StrContains('Hello', '!'))

    @patch('pkg.channel.library.come')
    async def test_come(self, mock_come):
        self.assertIs(await channel.commandCome(self.args), False)
        self.assertFalse(mock_come.called)
        mock_come.return_value = True
        self.permissions.inOwnerChannel = True
        self.assertIs(await channel.commandCome(self.args), True)
        mock_come.assert_called_once_with(self.database, 'botgotsthis',
                                          self.channel.send)

    @patch('pkg.channel.library.leave')
    async def test_leave(self, mock_leave):
        self.assertIs(await channel.commandLeave(self.args), False)
        self.assertFalse(mock_leave.called)
        mock_leave.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(await channel.commandLeave(self.args), True)
        mock_leave.assert_called_once_with('botgotsthis', self.channel.send)

    @patch('pkg.channel.library.auto_join')
    async def test_auto_join(self, mock_autojoin):
        self.assertIs(await channel.commandAutoJoin(self.args), False)
        self.assertFalse(mock_autojoin.called)
        mock_autojoin.return_value = True
        self.permissions.inOwnerChannel = True
        self.assertIs(await channel.commandAutoJoin(self.args), True)
        mock_autojoin.assert_called_once_with(
            self.database, 'botgotsthis', self.channel.send, self.args.message)
