from datetime import timedelta
from unittest.mock import patch

from source.data import CustomCommand, CommandActionTokens
from source.data.message import Message
from source.public.channel import custom
from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import IterableMatch, StrContains


class TestChannelCustomCustomCommand(TestChannel):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(message=Message('Kappa'))
        self.permissions.moderator = True
        self.permissions.chatModerator = False
        self.command = CustomCommand('Kappa', '#global', '')
        
        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.customMessageCooldown = 5
        self.mock_config.customMessageUserCooldown = 30
        
        patcher = patch('source.public.library.chat.inCooldown', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_channel_cooldown = patcher.start()
        self.mock_channel_cooldown.return_value = False
        
        patcher = patch('source.public.library.chat.in_user_cooldown',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_user_cooldown = patcher.start()
        self.mock_user_cooldown.return_value = False
        
        patcher = patch('source.public.library.timeout.record_timeout',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_timeout = patcher.start()
        
        patcher = patch('source.public.library.custom.get_command',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_command = patcher.start()
        self.mock_command.return_value = self.command
        
        patcher = patch('source.public.library.custom.create_messages',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_messages = patcher.start()
        self.mock_messages.return_value = []
        
    def test_nocustom(self):
        self.features.append('nocustom')
        self.assertIs(custom.customCommands(self.args), False)
        self.assertFalse(self.mock_command.called)
        self.assertFalse(self.mock_channel_cooldown.called)
        self.assertFalse(self.mock_user_cooldown.called)
        self.assertFalse(self.mock_messages.called)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.mock_timeout.called)

    def test_no_command(self):
        self.mock_command.return_value = None
        self.assertIs(custom.customCommands(self.args), False)
        self.mock_command.assert_called_once_with(
            self.database, 'kappa', 'botgotsthis', self.permissions)
        self.assertFalse(self.mock_messages.called)
        self.assertFalse(self.mock_channel_cooldown.called)
        self.assertFalse(self.mock_user_cooldown.called)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.mock_timeout.called)

    def test(self):
        self.assertIs(custom.customCommands(self.args), True)
        self.mock_command.assert_called_once_with(
            self.database, 'kappa', 'botgotsthis', self.permissions)
        self.mock_channel_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=5), 'customCommand', 'moderator')
        self.mock_user_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), 'customUserCommand', 'moderator')
        self.mock_messages.assert_called_once_with(self.command, self.args)
        self.channel.send.assert_called_once_with([])
        self.assertFalse(self.mock_timeout.called)

    def test_channel_cooldown(self):
        self.mock_channel_cooldown.return_value = True
        self.assertIs(custom.customCommands(self.args), False)
        self.mock_command.assert_called_once_with(
            self.database, 'kappa', 'botgotsthis', self.permissions)
        self.mock_channel_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=5), 'customCommand', 'moderator')
        self.assertFalse(self.mock_user_cooldown.called)
        self.assertFalse(self.mock_messages.called)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.mock_timeout.called)

    def test_user_cooldown(self):
        self.mock_user_cooldown.return_value = True
        self.assertIs(custom.customCommands(self.args), False)
        self.mock_command.assert_called_once_with(
            self.database, 'kappa', 'botgotsthis', self.permissions)
        self.mock_channel_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=5), 'customCommand', 'moderator')
        self.mock_user_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), 'customUserCommand', 'moderator')
        self.assertFalse(self.mock_messages.called)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.mock_timeout.called)

    def test_channel_moderator(self):
        self.permissions.chatModerator = True
        self.assertIs(custom.customCommands(self.args), True)
        self.mock_command.assert_called_once_with(
            self.database, 'kappa', 'botgotsthis', self.permissions)
        self.mock_channel_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=5), 'customCommand', 'moderator')
        self.mock_user_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), 'customUserCommand', 'moderator')
        self.mock_messages.assert_called_once_with(self.command, self.args)
        self.channel.send.assert_called_once_with([])
        self.mock_timeout.assert_called_once_with(
            self.database, self.channel, 'botgotsthis', [], 'Kappa', 'custom')


class TestChannelCustomCommand(TestChannel):
    def setUp(self):
        super().setUp()
        
        patcher = patch('source.public.channel.custom.process_command',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_process = patcher.start()
        
    def test_command(self):
        self.assertIs(custom.commandCommand(self.args), False)
        self.features.append('nocustom')
        self.permissionSet['moderator'] = True
        self.assertIs(custom.commandCommand(self.args), False)
        self.assertFalse(self.mock_process.called)
        self.features.clear()
        self.mock_process.return_value = True
        self.assertIs(custom.commandCommand(self.args), True)
        self.mock_process.assert_called_once_with(self.args, 'botgotsthis')

    def test_global(self):
        self.assertIs(custom.commandGlobal(self.args), False)
        self.assertFalse(self.mock_process.called)
        self.permissions.inOwnerChannel = True
        self.permissionSet['admin'] = True
        self.mock_process.return_value = True
        self.assertIs(custom.commandGlobal(self.args), True)
        self.mock_process.assert_called_once_with(self.args, '#global')


class TestChannelCustomProcessCommand(TestChannel):
    def setUp(self):
        super().setUp()
        self.message = Message('!commmand test !someCommand')
        self.args = self.args._replace(message=self.message)
        self.broadcaster = '#global'
        
        patcher = patch('source.public.library.custom.parse_action_message',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_input = patcher.start()
        self.mock_input.return_value = None

    def test_false(self):
        message = Message('')
        self.assertIs(
            custom.process_command(self.args._replace(message=message),
                                   self.broadcaster),
            False)
        self.assertFalse(self.mock_input.called)
        self.assertFalse(self.channel.send.called)

    def test(self):
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), False)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        self.assertFalse(self.channel.send.called)

    def test_level(self):
        self.mock_input.return_value = CommandActionTokens(
            'test', self.broadcaster, None, 'Kappa', '')
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Invalid level'))

    def test_level_permission(self):
        self.mock_input.return_value = CommandActionTokens(
            'test', self.broadcaster, 'moderator', 'Kappa', '')
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'permission', 'level'))

    def test_level_permission_wrong(self):
        self.mock_input.return_value = CommandActionTokens(
            'test', self.broadcaster, 'Kappa', 'Kappa', '')
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Invalid level'))

    def test_no_action(self):
        self.mock_input.return_value = CommandActionTokens(
            'test', self.broadcaster, '', 'Kappa', '')
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), False)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.custom.insert_command', autospec=True)
    def test_add(self, mock_insert):
        mock_insert.return_value = True
        input = CommandActionTokens('add', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_insert.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.custom.insert_command', autospec=True)
    def test_insert(self, mock_insert):
        mock_insert.return_value = True
        input = CommandActionTokens('insert', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_insert.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.custom.insert_command', autospec=True)
    def test_new(self, mock_insert):
        mock_insert.return_value = True
        input = CommandActionTokens('new', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_insert.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.custom.update_command', autospec=True)
    def test_update(self, mock_update):
        mock_update.return_value = True
        input = CommandActionTokens('update', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_update.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.custom.update_command', autospec=True)
    def test_edit(self, mock_update):
        mock_update.return_value = True
        input = CommandActionTokens('edit', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_update.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.custom.replace_command', autospec=True)
    def test_replace(self, mock_replace):
        mock_replace.return_value = True
        input = CommandActionTokens('replace', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_replace.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.custom.replace_command', autospec=True)
    def test_override(self, mock_replace):
        mock_replace.return_value = True
        input = CommandActionTokens('override', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_replace.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.custom.append_command', autospec=True)
    def test_append(self, mock_append):
        mock_append.return_value = True
        input = CommandActionTokens('append', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_append.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.custom.delete_command', autospec=True)
    def test_del(self, mock_delete):
        mock_delete.return_value = True
        input = CommandActionTokens('del', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_delete.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.custom.delete_command', autospec=True)
    def test_delete(self, mock_delete):
        mock_delete.return_value = True
        input = CommandActionTokens('delete', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_delete.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.custom.delete_command', autospec=True)
    def test_rem(self, mock_delete):
        mock_delete.return_value = True
        input = CommandActionTokens('rem', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_delete.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.custom.delete_command', autospec=True)
    def test_remove(self, mock_delete):
        mock_delete.return_value = True
        input = CommandActionTokens('remove', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_delete.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)
        
    @patch('source.public.channel.custom.command_property', autospec=True)
    def test_property(self, mock_property):
        mock_property.return_value = True
        input = CommandActionTokens('property', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            custom.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_property.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    def test_insert_command(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.insertCustomCommand.return_value = True
        self.assertIs(custom.insert_command(self.args, input), True)
        self.database.insertCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'add', 'success'))

    def test_insert_command_dberror(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.insertCustomCommand.return_value = False
        self.assertIs(custom.insert_command(self.args, input), True)
        self.database.insertCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'add', 'not', 'success'))

    def test_update_command(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.updateCustomCommand.return_value = True
        self.assertIs(custom.update_command(self.args, input), True)
        self.database.updateCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'update', 'success'))

    def test_update_command_dberror(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.updateCustomCommand.return_value = False
        self.assertIs(custom.update_command(self.args, input), True)
        self.database.updateCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'update', 'not', 'success'))

    def test_append_command(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.appendCustomCommand.return_value = True
        self.assertIs(custom.append_command(self.args, input), True)
        self.database.appendCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'append', 'success'))

    def test_append_command_dberror(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.appendCustomCommand.return_value = False
        self.assertIs(custom.append_command(self.args, input), True)
        self.database.appendCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'append', 'not', 'success'))

    def test_replace_command(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.replaceCustomCommand.return_value = True
        self.assertIs(custom.replace_command(self.args, input), True)
        self.database.replaceCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'replace', 'success'))

    def test_replace_command_dberror(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.replaceCustomCommand.return_value = False
        self.assertIs(custom.replace_command(self.args, input), True)
        self.database.replaceCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'replace', 'not', 'success'))

    def test_delete_command(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.deleteCustomCommand.return_value = True
        self.assertIs(custom.delete_command(self.args, input), True)
        self.database.deleteCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'remove', 'success'))

    def test_delete_command_dberror(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.deleteCustomCommand.return_value = False
        self.assertIs(custom.delete_command(self.args, input), True)
        self.database.deleteCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'remove', 'not', 'success'))

    def test_command_property_false(self):
        input = CommandActionTokens('', self.broadcaster, '', 'Kappa', '')
        self.assertIs(custom.command_property(self.args, input), False)
        self.permissionSet['broadcaster'] = True
        self.assertIs(custom.command_property(self.args, input), False)
        self.assertFalse(self.database.processCustomCommandProperty.called)
        self.assertFalse(self.channel.send.called)

    @patch('lists.custom', autospec=True)
    def test_command_property_empty(self, mock_list):
        mock_list.properties = []
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'someproperty PogChamp')
        self.permissionSet['broadcaster'] = True
        self.assertIs(custom.command_property(self.args, input), True)
        self.assertFalse(self.database.processCustomCommandProperty.called)
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'someproperty', 'property', 'not',
                        'exist'))

    @patch('lists.custom', autospec=True)
    def test_command_property(self, mock_list):
        mock_list.properties = ['someproperty']
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'someproperty PogChamp')
        self.database.processCustomCommandProperty.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(custom.command_property(self.args, input), True)
        self.database.processCustomCommandProperty.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'someproperty', 'PogChamp')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'someproperty', 'PogChamp',
                        'set'))

    @patch('lists.custom', autospec=True)
    def test_command_property_no_value(self, mock_list):
        mock_list.properties = ['someproperty']
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'someproperty')
        self.database.processCustomCommandProperty.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(custom.command_property(self.args, input), True)
        self.database.processCustomCommandProperty.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'someproperty', None)
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'someproperty', 'unset'))

    @patch('lists.custom', autospec=True)
    def test_command_property_dberror(self, mock_list):
        mock_list.properties = ['someproperty']
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'someproperty PogChamp')
        self.database.processCustomCommandProperty.return_value = False
        self.permissionSet['broadcaster'] = True
        self.assertIs(custom.command_property(self.args, input), True)
        self.database.processCustomCommandProperty.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'someproperty', 'PogChamp')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'someproperty', 'not'))

    @patch('bot.config')
    @patch('bot.utils.whisper')
    def test_raw_command(self, mock_whisper, mock_config):
        mock_config.messageLimit = 100
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.getCustomCommand.return_value = 'KappaRoss KappaPride'
        self.assertIs(custom.raw_command(self.args, input), True)
        self.database.getCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa')
        mock_whisper.assert_called_once_with(
            'botgotsthis',
            IterableMatch('KappaRoss KappaPride'))
        self.assertFalse(self.channel.send.called)

    @patch('bot.config')
    @patch('bot.utils.whisper')
    def test_raw_command_long(self, mock_whisper, mock_config):
        mock_config.messageLimit = 20
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.getCustomCommand.return_value = (
            'Kappa   Keepo KappaRoss KappaPride')
        self.assertIs(custom.raw_command(self.args, input), True)
        self.database.getCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa')
        mock_whisper.assert_called_once_with(
            'botgotsthis',
            IterableMatch('Kappa   Keepo', 'KappaRoss KappaPride'))
        self.assertFalse(self.channel.send.called)

    @patch('bot.config')
    @patch('bot.utils.whisper')
    def test_raw_command_not_exist(self, mock_whisper, mock_config):
        mock_config.messageLimit = 100
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.getCustomCommand.return_value = None
        self.assertIs(custom.raw_command(self.args, input), True)
        self.database.getCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'not', 'exist'))
        self.assertFalse(mock_whisper.called)
