from source.data.message import Message
from source.public.whisper import owner
from unittest.mock import ANY, patch
from unittests.public.test_whisper import TestWhisper


class TestWhisperOwner(TestWhisper):
    @patch('source.public.whisper.owner.utils.whisper', autospec=True)
    def test_hello(self, mock_whisper):
        self.assertIs(owner.commandHello(self.args), False)
        self.permissionSet['owner'] = True
        self.assertIs(owner.commandHello(self.args), True)
        mock_whisper.assert_called_once_with('botgotsthis', ANY)

    @patch('source.public.whisper.owner.exit.exit', autospec=True)
    def test_exit(self, mock_exit):
        self.assertIs(owner.commandExit(self.args), False)
        self.assertFalse(mock_exit.called)
        mock_exit.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        self.assertIs(owner.commandExit(self.args), True)
        mock_exit.assert_called_once_with(ANY)

    @patch('source.public.whisper.owner.channel.say', autospec=True)
    def test_say(self, mock_say):
        self.assertIs(owner.commandSay(self.args), False)
        self.assertFalse(mock_say.called)
        mock_say.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        message = Message('!say MeGotsThis Kappa')
        self.assertIs(owner.commandSay(self.args._replace(message=message)),
                      True)
        mock_say.assert_called_once_with(self.database, 'botgotsthis',
                                         'megotsthis', 'Kappa')

    @patch('source.public.whisper.owner.channel.join', autospec=True)
    def test_join(self, mock_join):
        self.assertIs(owner.commandJoin(self.args), False)
        self.assertFalse(mock_join.called)
        mock_join.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['admin'] = True
        message = Message('!join MeGotsThis')
        self.assertIs(owner.commandJoin(self.args._replace(message=message)),
                      True)
        mock_join.assert_called_once_with(self.database, 'megotsthis', ANY)

    @patch('source.public.whisper.owner.channel.part', autospec=True)
    def test_part(self, mock_part):
        self.assertIs(owner.commandPart(self.args), False)
        self.assertFalse(mock_part.called)
        mock_part.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['admin'] = True
        message = Message('!part MeGotsThis')
        self.assertIs(owner.commandPart(self.args._replace(message=message)),
                      True)
        mock_part.assert_called_once_with('megotsthis', ANY)

    @patch('source.public.whisper.owner.channel.empty_all', autospec=True)
    def test_empty_all(self, mock_empty_all):
        self.assertIs(owner.commandEmptyAll(self.args), False)
        self.assertFalse(mock_empty_all.called)
        mock_empty_all.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['admin'] = True
        self.assertIs(owner.commandEmptyAll(self.args), True)
        mock_empty_all.assert_called_once_with(ANY)

    @patch('source.public.whisper.owner.channel.empty', autospec=True)
    def test_empty(self, mock_empty):
        self.assertIs(owner.commandEmpty(self.args), False)
        self.assertFalse(mock_empty.called)
        mock_empty.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['admin'] = True
        self.assertIs(
            owner.commandEmpty(
                self.args._replace(message=Message('!emptychat MeGotsThis'))),
            True)
        mock_empty.assert_called_once_with('megotsthis', ANY)

    @patch('source.public.whisper.owner.managebot.manage_bot', autospec=True)
    def test_manage_bot(self, mock_manage_bot):
        self.assertIs(owner.commandManageBot(self.args), False)
        self.assertFalse(mock_manage_bot.called)
        mock_manage_bot.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        message = Message('!managebot listchats')
        self.assertIs(
            owner.commandManageBot(self.args._replace(message=message)), True)
        mock_manage_bot.assert_called_once_with(self.database, ANY,
                                                'botgotsthis', message)
