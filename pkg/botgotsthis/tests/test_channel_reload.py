from asynctest.mock import patch

from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import PartialMatch
from lib.data.message import Message

# Needs to be imported last
from ..library import reload as reload_library
from ..channel import reload


class TestChannelReload(TestChannel):
    @patch(reload_library.__name__ + '.full_reload')
    async def test_reload(self, mock_reload):
        self.assertIs(await reload.commandReload(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        self.assertIs(await reload.commandReload(self.args), True)
        mock_reload.assert_called_once_with(
            PartialMatch(self.channel.send, priority=0))

    @patch(reload_library.__name__ + '.reload_commands')
    async def test_reload_commands(self, mock_reload):
        self.assertIs(await reload.commandReloadCommands(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['manager'] = True
        self.assertIs(await reload.commandReloadCommands(self.args), True)
        mock_reload.assert_called_once_with(
            PartialMatch(self.channel.send, priority=0))

    @patch(reload_library.__name__ + '.reload_config')
    async def test_reload_config(self, mock_reload):
        self.assertIs(await reload.commandReloadConfig(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        self.assertIs(await reload.commandReloadConfig(self.args), True)
        mock_reload.assert_called_once_with(
            PartialMatch(self.channel.send, priority=0))

    @patch(reload_library.__name__ + '.refresh_cache')
    async def test_refresh_cache(self, mock_refresh):
        self.assertIs(await reload.commandRefreshCache(self.args), False)
        self.assertFalse(mock_refresh.called)
        mock_refresh.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        self.assertIs(await reload.commandRefreshCache(self.args), True)
        mock_refresh.assert_called_once_with(
            PartialMatch(self.channel.send, priority=0), self.data, None)

    @patch(reload_library.__name__ + '.refresh_cache')
    async def test_refresh_cache_keys(self, mock_refresh):
        mock_refresh.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        message = Message('!refreshcache *')
        self.args = self.args._replace(message=message)
        self.assertIs(await reload.commandRefreshCache(self.args), True)
        mock_refresh.assert_called_once_with(
            PartialMatch(self.channel.send, priority=0), self.data, '*')
