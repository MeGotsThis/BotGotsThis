from asynctest.mock import MagicMock, patch

from tests.unittest.base_channel import TestChannel
from lib.data.message import Message
from lib.database import DatabaseTimeout

# Needs to be imported last
from ..channel import purge


class TestModerationChannelPurge(TestChannel):
    @patch('lib.database.get_database')
    async def test_purge(self, mock_database):
        database = MagicMock(spec=DatabaseTimeout)
        mock_database.return_value = database
        database.__aenter__.return_value = database
        self.assertIs(await purge.commandPurge(self.args), False)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(database.recordTimeout.called)
        self.permissionSet['moderator'] = True
        self.permissionSet['chatModerator'] = True
        args = self.args._replace(message=Message('!purge MeGotsThis'))
        self.assertIs(await purge.commandPurge(args), True)
        self.channel.send.assert_called_once_with('.timeout MeGotsThis 1 ')
        database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', 'botgotsthis', 'purge', None, 1,
            '!purge MeGotsThis', None)

    @patch('lib.database.get_database')
    async def test_purge_reason(self, mock_database):
        database = MagicMock(spec=DatabaseTimeout)
        mock_database.return_value = database
        database.__aenter__.return_value = database
        self.permissionSet['moderator'] = True
        self.permissionSet['chatModerator'] = True
        args = self.args._replace(message=Message('!purge MeGotsThis Kappa'))
        self.assertIs(await purge.commandPurge(args), True)
        self.channel.send.assert_called_once_with(
            '.timeout MeGotsThis 1 Kappa')
        database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', 'botgotsthis', 'purge', None, 1,
            '!purge MeGotsThis Kappa', 'Kappa')
