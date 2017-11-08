from asynctest.mock import patch

from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import StrContains
from lib.data.message import Message

# Needs to be imported last
from ..library import chat as library_chat
from ..channel import chat


class TestChannelBroadcaster(TestChannel):
    async def test_permit(self):
        self.channel.channel = 'megotsthis'
        self.data.isPermittedUser.return_value = False
        self.assertIs(await chat.commandPermit(self.args), False)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.data.isPermittedUser.called)
        self.assertFalse(self.data.addPermittedUser.called)
        self.assertFalse(self.data.removePermittedUser.called)

    async def test_permit_add(self):
        self.channel.channel = 'megotsthis'
        self.data.isPermittedUser.return_value = False
        self.data.addPermittedUser.return_value = True
        self.permissionSet['moderator'] = True
        args = self.args._replace(message=Message('!permit MeBotsThis'))
        self.assertIs(await chat.commandPermit(args), True)
        self.assertTrue(self.data.isPermittedUser.called)
        self.assertTrue(self.data.addPermittedUser.called)
        self.assertFalse(self.data.removePermittedUser.called)
        self.channel.send.assert_called_once_with(
            StrContains('botgotsthis', 'mebotsthis', 'permitted',
                        'megotsthis'))

    async def test_permit_remove(self):
        self.channel.channel = 'megotsthis'
        self.data.isPermittedUser.return_value = True
        self.data.removePermittedUser.return_value = True
        self.permissionSet['moderator'] = True
        args = self.args._replace(message=Message('!permit MeBotsThis'))
        self.assertIs(await chat.commandPermit(args), True)
        self.assertTrue(self.data.isPermittedUser.called)
        self.assertTrue(self.data.removePermittedUser.called)
        self.assertFalse(self.data.addPermittedUser.called)
        self.channel.send.assert_called_once_with(
            StrContains('botgotsthis', 'mebotsthis', 'unpermitted',
                        'megotsthis'))

    @patch(library_chat.__name__ + '.empty')
    async def test_empty(self, mock_empty):
        self.assertIs(await chat.commandEmpty(self.args), False)
        self.assertFalse(mock_empty.called)
        mock_empty.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(await chat.commandEmpty(self.args), True)
        mock_empty.assert_called_once_with('botgotsthis', self.channel.send)

    @patch(library_chat.__name__ + '.set_timeout_level')
    async def test_set_timeout_level(self, mock_set_timeout):
        self.assertIs(await chat.commandSetTimeoutLevel(self.args),
                      False)
        self.assertFalse(mock_set_timeout.called)
        mock_set_timeout.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(await chat.commandSetTimeoutLevel(self.args),
                      True)
        mock_set_timeout.assert_called_once_with(
            self.data, 'botgotsthis', self.channel.send, self.args.message)
