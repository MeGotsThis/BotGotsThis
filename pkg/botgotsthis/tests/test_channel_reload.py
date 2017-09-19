from asynctest.mock import patch

from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import PartialMatch

# Needs to be imported last
from pkg.botgotsthis.channel import reload


class TestChannelReload(TestChannel):
    @patch('pkg.botgotsthis.library.reload.full_reload')
    async def test_reload(self, mock_reload):
        self.assertIs(await reload.commandReload(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        self.assertIs(await reload.commandReload(self.args), True)
        mock_reload.assert_called_once_with(
            PartialMatch(self.channel.send, priority=0))

    @patch('pkg.botgotsthis.library.reload.reload_commands')
    async def test_reload_commands(self, mock_reload):
        self.assertIs(await reload.commandReloadCommands(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['manager'] = True
        self.assertIs(await reload.commandReloadCommands(self.args), True)
        mock_reload.assert_called_once_with(
            PartialMatch(self.channel.send, priority=0))

    @patch('pkg.botgotsthis.library.reload.reload_config')
    async def test_reload_config(self, mock_reload):
        self.assertIs(await reload.commandReloadConfig(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        self.assertIs(await reload.commandReloadConfig(self.args), True)
        mock_reload.assert_called_once_with(
            PartialMatch(self.channel.send, priority=0))
