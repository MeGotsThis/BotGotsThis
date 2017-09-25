from asynctest.mock import patch

from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import StrContains
from lib.data.message import Message

# Needs to be imported last
from ..channel import chat


class TestChannelBroadcaster(TestChannel):
    async def test_permit(self):
        self.channel.channel = 'megotsthis'
        self.database.isPermittedUser.return_value = False
        self.assertIs(await chat.commandPermit(self.args), False)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.database.isPermittedUser.called)
        self.assertFalse(self.database.addPermittedUser.called)
        self.assertFalse(self.database.removePermittedUser.called)

    async def test_permit_add(self):
        self.channel.channel = 'megotsthis'
        self.database.isPermittedUser.return_value = False
        self.database.addPermittedUser.return_value = True
        self.permissionSet['moderator'] = True
        args = self.args._replace(message=Message('!permit MeBotsThis'))
        self.assertIs(await chat.commandPermit(args), True)
        self.assertTrue(self.database.isPermittedUser.called)
        self.assertTrue(self.database.addPermittedUser.called)
        self.assertFalse(self.database.removePermittedUser.called)
        self.channel.send.assert_called_once_with(
            StrContains('botgotsthis', 'mebotsthis', 'permitted',
                        'megotsthis'))

    async def test_permit_remove(self):
        self.channel.channel = 'megotsthis'
        self.database.isPermittedUser.return_value = True
        self.database.removePermittedUser.return_value = True
        self.permissionSet['moderator'] = True
        args = self.args._replace(message=Message('!permit MeBotsThis'))
        self.assertIs(await chat.commandPermit(args), True)
        self.assertTrue(self.database.isPermittedUser.called)
        self.assertTrue(self.database.removePermittedUser.called)
        self.assertFalse(self.database.addPermittedUser.called)
        self.channel.send.assert_called_once_with(
            StrContains('botgotsthis', 'mebotsthis', 'unpermitted',
                        'megotsthis'))

    @patch('pkg.botgotsthis.library.chat.empty')
    async def test_empty(self, mock_empty):
        self.assertIs(await chat.commandEmpty(self.args), False)
        self.assertFalse(mock_empty.called)
        mock_empty.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(await chat.commandEmpty(self.args), True)
        mock_empty.assert_called_once_with('botgotsthis', self.channel.send)

    @patch('pkg.botgotsthis.library.chat.set_timeout_level')
    async def test_set_timeout_level(self, mock_set_timeout):
        self.assertIs(await chat.commandSetTimeoutLevel(self.args),
                      False)
        self.assertFalse(mock_set_timeout.called)
        mock_set_timeout.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(await chat.commandSetTimeoutLevel(self.args),
                      True)
        mock_set_timeout.assert_called_once_with(
            self.database, 'botgotsthis', self.channel.send, self.args.message)
