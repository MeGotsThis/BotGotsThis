from datetime import timedelta

from asynctest.mock import patch

from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import IterableMatch, StrContains

# Needs to be imported last
from lib.data import CustomCommand, CommandActionTokens
from lib.data.message import Message
from .. import library
from .. import channel


class TestCustomCommandChannelCustomCommands(TestChannel):
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

        patcher = patch('lib.helper.chat.inCooldown', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_channel_cooldown = patcher.start()
        self.mock_channel_cooldown.return_value = False

        patcher = patch('lib.helper.chat.in_user_cooldown', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_user_cooldown = patcher.start()
        self.mock_user_cooldown.return_value = False

        patcher = patch('lib.helper.timeout.record_timeout')
        self.addCleanup(patcher.stop)
        self.mock_timeout = patcher.start()

        patcher = patch(library.__name__ + '.get_command')
        self.addCleanup(patcher.stop)
        self.mock_command = patcher.start()
        self.mock_command.return_value = self.command

        patcher = patch(library.__name__ + '.create_messages')
        self.addCleanup(patcher.stop)
        self.mock_messages = patcher.start()
        self.mock_messages.return_value = []

    async def test_nocustom(self):
        self.features.append('nocustom')
        self.assertIs(await channel.customCommands(self.args), False)
        self.assertFalse(self.mock_command.called)
        self.assertFalse(self.mock_channel_cooldown.called)
        self.assertFalse(self.mock_user_cooldown.called)
        self.assertFalse(self.mock_messages.called)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_no_command(self):
        self.mock_command.return_value = None
        self.assertIs(await channel.customCommands(self.args), False)
        self.mock_command.assert_called_once_with(
            self.database, 'kappa', 'botgotsthis', self.permissions)
        self.assertFalse(self.mock_messages.called)
        self.assertFalse(self.mock_channel_cooldown.called)
        self.assertFalse(self.mock_user_cooldown.called)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.mock_timeout.called)

    async def test(self):
        self.assertIs(await channel.customCommands(self.args), True)
        self.mock_command.assert_called_once_with(
            self.database, 'kappa', 'botgotsthis', self.permissions)
        self.mock_channel_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=5), 'customCommand', 'moderator')
        self.mock_user_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), 'customUserCommand', 'moderator')
        self.mock_messages.assert_called_once_with(self.command, self.args)
        self.channel.send.assert_called_once_with([])
        self.assertFalse(self.mock_timeout.called)

    async def test_channel_cooldown(self):
        self.mock_channel_cooldown.return_value = True
        self.assertIs(await channel.customCommands(self.args), False)
        self.mock_command.assert_called_once_with(
            self.database, 'kappa', 'botgotsthis', self.permissions)
        self.mock_channel_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=5), 'customCommand', 'moderator')
        self.assertFalse(self.mock_user_cooldown.called)
        self.assertFalse(self.mock_messages.called)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_user_cooldown(self):
        self.mock_user_cooldown.return_value = True
        self.assertIs(await channel.customCommands(self.args), False)
        self.mock_command.assert_called_once_with(
            self.database, 'kappa', 'botgotsthis', self.permissions)
        self.mock_channel_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=5), 'customCommand', 'moderator')
        self.mock_user_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), 'customUserCommand', 'moderator')
        self.assertFalse(self.mock_messages.called)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_channel_moderator(self):
        self.permissions.chatModerator = True
        self.assertIs(await channel.customCommands(self.args), True)
        self.mock_command.assert_called_once_with(
            self.database, 'kappa', 'botgotsthis', self.permissions)
        self.mock_channel_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=5), 'customCommand', 'moderator')
        self.mock_user_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), 'customUserCommand', 'moderator')
        self.mock_messages.assert_called_once_with(self.command, self.args)
        self.channel.send.assert_called_once_with([])
        self.mock_timeout.assert_called_once_with(
            self.channel, 'botgotsthis', [], 'Kappa', 'custom')


class TestCustomCommandChannelCustomCommand(TestChannel):
    def setUp(self):
        super().setUp()

        patcher = patch(channel.__name__ + '.process_command')
        self.addCleanup(patcher.stop)
        self.mock_process = patcher.start()

    async def test_command(self):
        self.assertIs(await channel.commandCommand(self.args), False)
        self.features.append('nocustom')
        self.permissionSet['moderator'] = True
        self.assertIs(await channel.commandCommand(self.args), False)
        self.assertFalse(self.mock_process.called)
        self.features.clear()
        self.mock_process.return_value = True
        self.assertIs(await channel.commandCommand(self.args), True)
        self.mock_process.assert_called_once_with(self.args, 'botgotsthis')

    async def test_global(self):
        self.assertIs(await channel.commandGlobal(self.args), False)
        self.assertFalse(self.mock_process.called)
        self.permissions.inOwnerChannel = True
        self.permissionSet['admin'] = True
        self.mock_process.return_value = True
        self.assertIs(await channel.commandGlobal(self.args), True)
        self.mock_process.assert_called_once_with(self.args, '#global')


class TestCustomCommandChannelCustomProcessCommand(TestChannel):
    def setUp(self):
        super().setUp()
        self.message = Message('!commmand test !someCommand')
        self.args = self.args._replace(message=self.message)
        self.broadcaster = '#global'

        patcher = patch(library.__name__ + '.parse_action_message',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_input = patcher.start()
        self.mock_input.return_value = None

    async def test_false(self):
        message = Message('')
        self.assertIs(
            await channel.process_command(
                self.args._replace(message=message), self.broadcaster),
            False)
        self.assertFalse(self.mock_input.called)
        self.assertFalse(self.channel.send.called)

    async def test(self):
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), False)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        self.assertFalse(self.channel.send.called)

    async def test_level_access(self):
        self.mock_input.return_value = CommandActionTokens(
            'test', self.broadcaster, None, 'Kappa', '')
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Invalid level'))

    async def test_level_permission(self):
        self.mock_input.return_value = CommandActionTokens(
            'test', self.broadcaster, 'moderator', 'Kappa', '')
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'permission', 'level'))

    async def test_level_permission_wrong(self):
        self.mock_input.return_value = CommandActionTokens(
            'test', self.broadcaster, 'Kappa', 'Kappa', '')
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Invalid level'))

    async def test_no_action(self):
        self.mock_input.return_value = CommandActionTokens(
            'test', self.broadcaster, '', 'Kappa', '')
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), False)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.insert_command')
    async def test_add(self, mock_insert):
        mock_insert.return_value = True
        input = CommandActionTokens('add', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_insert.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.insert_command')
    async def test_insert(self, mock_insert):
        mock_insert.return_value = True
        input = CommandActionTokens('insert', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_insert.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.insert_command')
    async def test_new(self, mock_insert):
        mock_insert.return_value = True
        input = CommandActionTokens('new', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_insert.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.update_command')
    async def test_update(self, mock_update):
        mock_update.return_value = True
        input = CommandActionTokens('update', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_update.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.update_command')
    async def test_edit(self, mock_update):
        mock_update.return_value = True
        input = CommandActionTokens('edit', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_update.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.replace_command')
    async def test_replace(self, mock_replace):
        mock_replace.return_value = True
        input = CommandActionTokens('replace', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_replace.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.replace_command')
    async def test_override(self, mock_replace):
        mock_replace.return_value = True
        input = CommandActionTokens('override', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_replace.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.append_command')
    async def test_append(self, mock_append):
        mock_append.return_value = True
        input = CommandActionTokens('append', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_append.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.delete_command')
    async def test_del(self, mock_delete):
        mock_delete.return_value = True
        input = CommandActionTokens('del', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_delete.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.delete_command')
    async def test_delete(self, mock_delete):
        mock_delete.return_value = True
        input = CommandActionTokens('delete', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_delete.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.delete_command')
    async def test_rem(self, mock_delete):
        mock_delete.return_value = True
        input = CommandActionTokens('rem', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_delete.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.delete_command')
    async def test_remove(self, mock_delete):
        mock_delete.return_value = True
        input = CommandActionTokens('remove', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_delete.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.command_property')
    async def test_property(self, mock_property):
        mock_property.return_value = True
        input = CommandActionTokens('property', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_property.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.raw_command')
    async def test_raw(self, mock_raw):
        mock_raw.return_value = True
        input = CommandActionTokens('raw', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_raw.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.raw_command')
    async def test_original(self, mock_raw):
        mock_raw.return_value = True
        input = CommandActionTokens('original', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_raw.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.level_command')
    async def test_level(self, mock_level):
        mock_level.return_value = True
        input = CommandActionTokens('level', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_level.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    @patch(channel.__name__ + '.rename_command')
    async def test_rename(self, mock_rename):
        mock_rename.return_value = True
        input = CommandActionTokens('rename', self.broadcaster, '', '', '')
        self.mock_input.return_value = input
        self.assertIs(
            await channel.process_command(self.args, self.broadcaster), True)
        self.mock_input.assert_called_once_with(self.message, self.broadcaster)
        mock_rename.assert_called_once_with(self.args, input)
        self.assertFalse(self.channel.send.called)

    async def test_insert_command(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.insertCustomCommand.return_value = True
        self.assertIs(await channel.insert_command(self.args, input), True)
        self.database.insertCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'add', 'success'))

    async def test_insert_command_dberror(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.insertCustomCommand.return_value = False
        self.assertIs(await channel.insert_command(self.args, input), True)
        self.database.insertCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'add', 'not', 'success'))

    async def test_update_command(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.updateCustomCommand.return_value = True
        self.assertIs(await channel.update_command(self.args, input), True)
        self.database.updateCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'update', 'success'))

    async def test_update_command_dberror(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.updateCustomCommand.return_value = False
        self.assertIs(await channel.update_command(self.args, input), True)
        self.database.updateCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'update', 'not', 'success'))

    async def test_append_command(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.appendCustomCommand.return_value = True
        self.assertIs(await channel.append_command(self.args, input), True)
        self.database.appendCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'append', 'success'))

    async def test_append_command_dberror(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.appendCustomCommand.return_value = False
        self.assertIs(await channel.append_command(self.args, input), True)
        self.database.appendCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'append', 'not', 'success'))

    async def test_replace_command(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.replaceCustomCommand.return_value = True
        self.assertIs(await channel.replace_command(self.args, input), True)
        self.database.replaceCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'replace', 'success'))

    async def test_replace_command_dberror(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.replaceCustomCommand.return_value = False
        self.assertIs(await channel.replace_command(self.args, input), True)
        self.database.replaceCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'PogChamp', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'replace', 'not', 'success'))

    async def test_delete_command(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.deleteCustomCommand.return_value = True
        self.assertIs(await channel.delete_command(self.args, input), True)
        self.database.deleteCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'remove', 'success'))

    async def test_delete_command_dberror(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.deleteCustomCommand.return_value = False
        self.assertIs(await channel.delete_command(self.args, input), True)
        self.database.deleteCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'botgotsthis')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'remove', 'not', 'success'))

    async def test_command_property_false(self):
        input = CommandActionTokens('', self.broadcaster, '', 'Kappa', '')
        self.assertIs(await channel.command_property(self.args, input), False)
        self.permissionSet['broadcaster'] = True
        self.assertIs(await channel.command_property(self.args, input), False)
        self.assertFalse(self.database.processCustomCommandProperty.called)
        self.assertFalse(self.channel.send.called)

    @patch('lib.items.custom', autospec=True)
    async def test_command_property_empty(self, mock_list):
        mock_list.properties.return_value = []
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'someproperty PogChamp')
        self.permissionSet['broadcaster'] = True
        self.assertIs(await channel.command_property(self.args, input), True)
        self.assertFalse(self.database.processCustomCommandProperty.called)
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'someproperty', 'property', 'not',
                        'exist'))

    @patch('lib.items.custom', autospec=True)
    async def test_command_property(self, mock_list):
        mock_list.properties.return_value = ['someproperty']
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'someproperty PogChamp')
        self.database.processCustomCommandProperty.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(await channel.command_property(self.args, input), True)
        self.database.processCustomCommandProperty.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'someproperty', 'PogChamp')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'someproperty', 'PogChamp',
                        'set'))

    @patch('lib.items.custom', autospec=True)
    async def test_command_property_no_value(self, mock_list):
        mock_list.properties.return_value = ['someproperty']
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'someproperty')
        self.database.processCustomCommandProperty.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(await channel.command_property(self.args, input), True)
        self.database.processCustomCommandProperty.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'someproperty', None)
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'someproperty', 'unset'))

    @patch('lib.items.custom', autospec=True)
    async def test_command_property_dberror(self, mock_list):
        mock_list.properties.return_value = ['someproperty']
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'someproperty PogChamp')
        self.database.processCustomCommandProperty.return_value = False
        self.permissionSet['broadcaster'] = True
        self.assertIs(await channel.command_property(self.args, input), True)
        self.database.processCustomCommandProperty.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'someproperty', 'PogChamp')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'someproperty', 'not'))

    @patch('bot.config')
    @patch('bot.utils.whisper')
    async def test_raw_command(self, mock_whisper, mock_config):
        mock_config.messageLimit = 100
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.getCustomCommand.return_value = 'KappaRoss KappaPride'
        self.assertIs(await channel.raw_command(self.args, input), True)
        self.database.getCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa')
        mock_whisper.assert_called_once_with(
            'botgotsthis',
            IterableMatch('KappaRoss KappaPride'))
        self.assertFalse(self.channel.send.called)

    @patch('bot.config')
    @patch('bot.utils.whisper')
    async def test_raw_command_long(self, mock_whisper, mock_config):
        mock_config.messageLimit = 20
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.getCustomCommand.return_value = (
            'Kappa   Keepo KappaRoss KappaPride')
        self.assertIs(await channel.raw_command(self.args, input), True)
        self.database.getCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa')
        mock_whisper.assert_called_once_with(
            'botgotsthis',
            IterableMatch('Kappa   Keepo', 'KappaRoss KappaPride'))
        self.assertFalse(self.channel.send.called)

    @patch('bot.config')
    @patch('bot.utils.whisper')
    async def test_raw_command_not_exist(self, mock_whisper, mock_config):
        mock_config.messageLimit = 100
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.getCustomCommand.return_value = None
        self.assertIs(await channel.raw_command(self.args, input), True)
        self.database.getCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'not', 'exist'))
        self.assertFalse(mock_whisper.called)

    async def test_level_command(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'mod')
        self.database.levelCustomCommand.return_value = True
        self.assertIs(await channel.level_command(self.args, input), True)
        self.database.levelCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'botgotsthis', 'moderator')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'change', 'success'))

    async def test_level_command_capitals(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'BrOaDcAsTeR')
        self.database.levelCustomCommand.return_value = True
        self.assertIs(await channel.level_command(self.args, input), True)
        self.database.levelCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'botgotsthis', 'broadcaster')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'change', 'success'))

    async def test_level_command_unknown_level(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp DansGame')
        self.database.levelCustomCommand.return_value = True
        self.assertIs(await channel.level_command(self.args, input), True)
        self.assertFalse(self.database.levelCustomCommand.called)
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'PogChamp DansGame', 'invalid',
                        'permission'))

    async def test_level_command_dberror(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'moderator')
        self.database.levelCustomCommand.return_value = False
        self.assertIs(await channel.level_command(self.args, input), True)
        self.database.levelCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'botgotsthis', 'moderator')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'change', 'not', 'success'))

    async def test_rename_command(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.renameCustomCommand.return_value = True
        self.assertIs(await channel.rename_command(self.args, input), True)
        self.database.renameCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'botgotsthis', 'PogChamp')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'rename', 'success',
                        'PogChamp'))

    async def test_rename_command_multiple(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp DansGame')
        self.database.renameCustomCommand.return_value = True
        self.assertIs(await channel.rename_command(self.args, input), True)
        self.database.renameCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'botgotsthis', 'PogChamp')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'rename', 'success',
                        'PogChamp'))

    async def test_rename_command_blank(self):
        input = CommandActionTokens('', self.broadcaster, '', 'Kappa', '')
        self.assertIs(await channel.rename_command(self.args, input), True)
        self.assertFalse(self.database.renameCustomCommand.called)
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'specify', 'command', 'rename'))

    async def test_rename_command_dberror(self):
        input = CommandActionTokens('', self.broadcaster, '',
                                    'Kappa', 'PogChamp')
        self.database.renameCustomCommand.return_value = False
        self.assertIs(await channel.rename_command(self.args, input), True)
        self.database.renameCustomCommand.assert_called_once_with(
            self.broadcaster, '', 'Kappa', 'botgotsthis', 'PogChamp')
        self.channel.send.assert_called_once_with(
            StrContains(self.args.nick, 'Kappa', 'rename', 'not', 'success',
                        'PogChamp'))
