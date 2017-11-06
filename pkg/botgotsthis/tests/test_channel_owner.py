from asynctest.mock import patch

from tests.unittest.base_channel import TestChannel
from lib.data.message import Message
from tests.unittest.mock_class import PartialMatch

# Needs to be imported last
from ..library import channel, exit, managebot
from ..channel import owner


class TestChannelOwner(TestChannel):
    @patch(exit.__name__ + '.exit')
    async def test_exit(self, mock_exit):
        self.assertIs(await owner.commandExit(self.args), False)
        self.assertFalse(mock_exit.called)
        mock_exit.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        self.assertIs(await owner.commandExit(self.args), True)
        mock_exit.assert_called_once_with(
            PartialMatch(self.channel.send, priority=0))

    @patch(channel.__name__ + '.say')
    async def test_say(self, mock_say):
        self.assertIs(await owner.commandSay(self.args), False)
        self.assertFalse(mock_say.called)
        mock_say.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        args = self.args._replace(message=Message('!say MeGotsThis Kappa'))
        self.assertIs(await owner.commandSay(args), True)
        mock_say.assert_called_once_with('botgotsthis', 'megotsthis', 'Kappa')

    @patch(channel.__name__ + '.join')
    async def test_join(self, mock_join):
        self.assertIs(await owner.commandJoin(self.args), False)
        self.assertFalse(mock_join.called)
        mock_join.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['admin'] = True
        args = self.args._replace(message=Message('!join MeGotsThis'))
        self.assertIs(await owner.commandJoin(args), True)
        mock_join.assert_called_once_with('megotsthis', self.channel.send)

    @patch(channel.__name__ + '.part')
    async def test_part(self, mock_part):
        self.assertIs(await owner.commandPart(self.args), False)
        self.assertFalse(mock_part.called)
        mock_part.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['admin'] = True
        args = self.args._replace(message=Message('!part MeGotsThis'))
        self.assertIs(await owner.commandPart(args), True)
        mock_part.assert_called_once_with('megotsthis', self.channel.send)

    @patch(channel.__name__ + '.empty_all')
    async def test_empty_all(self, mock_empty_all):
        self.assertIs(await owner.commandEmptyAll(self.args), False)
        self.assertFalse(mock_empty_all.called)
        mock_empty_all.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['admin'] = True
        self.assertIs(await owner.commandEmptyAll(self.args), True)
        mock_empty_all.assert_called_once_with(self.channel.send)

    @patch(channel.__name__ + '.empty')
    async def test_empty(self, mock_empty):
        self.assertIs(await owner.commandEmpty(self.args), False)
        self.assertFalse(mock_empty.called)
        mock_empty.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['admin'] = True
        args = self.args._replace(message=Message('!emptychat MeGotsThis'))
        self.assertIs(await owner.commandEmpty(args), True)
        mock_empty.assert_called_once_with('megotsthis', self.channel.send)

    @patch(managebot.__name__ + '.manage_bot')
    async def test_manage_bot(self, mock_manage_bot):
        self.assertIs(await owner.commandManageBot(self.args), False)
        self.assertFalse(mock_manage_bot.called)
        mock_manage_bot.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['manager'] = True
        message = Message('!managebot listchats')
        args = self.args._replace(message=message)
        self.assertIs(await owner.commandManageBot(args), True)
        mock_manage_bot.assert_called_once_with(
            self.data, self.permissions, self.channel.send,
            'botgotsthis', message)
