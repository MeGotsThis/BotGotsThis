from tests.unittest.base_channel import TestChannel
from lib.data.message import Message
from tests.unittest.mock_class import StrContains

# Needs to be imported last
from pkg.botgotsthis.channel import mod


class TestChannelMod(TestChannel):
    async def test_permit(self):
        self.channel.channel = 'megotsthis'
        self.database.isPermittedUser.return_value = False
        self.assertIs(await mod.commandPermit(self.args), False)
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
        self.assertIs(await mod.commandPermit(args), True)
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
        self.assertIs(await mod.commandPermit(args), True)
        self.assertTrue(self.database.isPermittedUser.called)
        self.assertTrue(self.database.removePermittedUser.called)
        self.assertFalse(self.database.addPermittedUser.called)
        self.channel.send.assert_called_once_with(
            StrContains('botgotsthis', 'mebotsthis', 'unpermitted',
                        'megotsthis'))
