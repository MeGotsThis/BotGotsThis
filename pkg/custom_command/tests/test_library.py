import unittest

import asynctest

from collections import defaultdict
from datetime import datetime

from asynctest.mock import CoroutineMock, MagicMock, Mock, call, patch

from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from lib.cache import CacheStore
from lib.data import ChatCommandArgs, CommandActionTokens
from lib.data import CustomCommand, CustomFieldArgs, CustomFieldParts
from lib.data import CustomProcessArgs
from lib.data.message import Message
from lib.data.permissions import ChatPermissionSet
from lib.database import DatabaseMain
from tests.unittest.mock_class import TypeMatch
from .. import library


class TestCustomCommandLibraryCustomGetCommand(asynctest.TestCase):
    def setUp(self):
        self.data = Mock(spec=CacheStore)
        self.database = Mock(spec=DatabaseMain)
        self.permissions = defaultdict(lambda: False, {'': True})

    async def test_no_commands(self):
        self.data.getChatCommands.return_value = {
            'botgotsthis': {}, '#global': {}}
        self.assertIsNone(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_public_command(self):
        self.data.getChatCommands.return_value = {
            'botgotsthis': {'': 'Kappa'}, '#global': {}}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand('Kappa', 'botgotsthis', ''))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_subscriber(self):
        self.permissions['subscriber'] = True
        self.data.getChatCommands.return_value = {
            'botgotsthis': {'subscriber': 'Kappa'}, '#global': {}}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand('Kappa', 'botgotsthis', 'subscriber'))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_moderator(self):
        self.permissions['moderator'] = True
        self.data.getChatCommands.return_value = {
            'botgotsthis': {'moderator': 'Kappa'}, '#global': {}}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand('Kappa', 'botgotsthis', 'moderator'))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_broadcaster(self):
        self.permissions['broadcaster'] = True
        self.data.getChatCommands.return_value = {
            'botgotsthis': {'broadcaster': 'Kappa'}, '#global': {}}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand('Kappa', 'botgotsthis', 'broadcaster'))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_globalMod(self):
        self.permissions['globalMod'] = True
        self.data.getChatCommands.return_value = {
            'botgotsthis': {'globalMod': 'Kappa'}, '#global': {}}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand('Kappa', 'botgotsthis', 'globalMod'))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_admin(self):
        self.permissions['admin'] = True
        self.data.getChatCommands.return_value = {
            'botgotsthis': {'admin': 'Kappa'}, '#global': {}}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand('Kappa', 'botgotsthis', 'admin'))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_staff(self):
        self.permissions['staff'] = True
        self.data.getChatCommands.return_value = {
            'botgotsthis': {'staff': 'Kappa'}, '#global': {}}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand('Kappa', 'botgotsthis', 'staff'))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_owner(self):
        self.permissions['owner'] = True
        self.data.getChatCommands.return_value = {
            'botgotsthis': {'owner': 'Kappa'}, '#global': {}}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand('Kappa', 'botgotsthis', 'owner'))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_global_command(self):
        self.data.getChatCommands.return_value = {
            'botgotsthis': {}, '#global': {'': 'Kappa'}}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand('Kappa', '#global', ''))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_public_global_command(self):
        self.data.getChatCommands.return_value = {
            'botgotsthis': {'': 'KappaPride'}, '#global': {'': 'KappaRoss'}}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand('KappaPride', 'botgotsthis', ''))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_no_access(self):
        self.data.getChatCommands.return_value = {
            'botgotsthis': {'moderator': 'KappaPride'}, '#global': {}}
        self.assertIsNone(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_multiple_permissions(self):
        self.permissions['turbo'] = True
        self.permissions['subscriber'] = True
        self.permissions['moderator'] = True
        self.permissions['broadcaster'] = True
        self.data.getChatCommands.return_value = {
            'botgotsthis': {
                '': 'Kappa',
                'turbo': 'KappaClaus',
                'subscriber': 'KappaRoss',
                'moderator': 'KappaPride',
                'broadcaster': 'KappaHD',
                'owner': 'FrankerZ',
                },
            '#global': {}}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand('KappaHD', 'botgotsthis', 'broadcaster'))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_multiple_permissions_with_global(self):
        self.permissions['turbo'] = True
        self.permissions['subscriber'] = True
        self.permissions['moderator'] = True
        self.permissions['broadcaster'] = True
        self.data.getChatCommands.return_value = {
            'botgotsthis': {
                '': 'Kappa',
                'turbo': 'KappaClaus',
                'subscriber': 'KappaRoss',
                'moderator': 'KappaPride',
                },
            '#global': {
                '': ':(',
                'turbo': ':s',
                'subscriber': ':o',
                'moderator': 'R)',
                'broadcaster': ':)',
            }}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand(':)', '#global', 'broadcaster'))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')

    async def test_multiple_permissions_with_channel(self):
        self.permissions['turbo'] = True
        self.permissions['subscriber'] = True
        self.permissions['moderator'] = True
        self.permissions['broadcaster'] = True
        self.data.getChatCommands.return_value = {
            'botgotsthis': {
                '': 'Kappa',
                'turbo': 'KappaClaus',
                'subscriber': 'KappaRoss',
                'moderator': 'KappaPride',
                'broadcaster': 'KappaHD',
                },
            '#global': {
                '': ':(',
                'turbo': ':s',
                'subscriber': ':o',
                'moderator': 'R)',
                'broadcaster': ':)',
            }}
        self.assertEqual(
            await library.get_command(self.data, '!kappa', 'botgotsthis',
                                      self.permissions),
            CustomCommand('KappaHD', 'botgotsthis', 'broadcaster'))
        self.data.getChatCommands.assert_called_once_with(
            'botgotsthis', '!kappa')


class TestCustomCommandLibraryCustomCreateMessages(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.tags = IrcMessageTags()
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.data = Mock(spec=CacheStore)
        self.data.hasFeature.return_value = False
        self.database = Mock(spec=DatabaseMain)
        self.database.hasFeature.return_value = False
        self.permissions = MagicMock(spec=ChatPermissionSet)
        self.command = CustomCommand('Kappa KappaRoss KappaPride',
                                     '#global', '')
        self.args = ChatCommandArgs(
            self.data, self.database, self.channel, self.tags, 'botgotsthis',
            Message('Kappa'), self.permissions, self.now)

        patcher = patch(library.__name__ + '.split_message',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_split = patcher.start()

        patcher = patch(library.__name__ + '.convert_field')
        self.addCleanup(patcher.stop)
        self.mock_convert = patcher.start()
        self.mock_convert.side_effect = lambda args: args.default

        patcher = patch(library.__name__ + '.format', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_format = patcher.start()
        self.mock_format.side_effect = lambda string, format, has: string

        patcher = patch('lib.items.custom', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_list = patcher.start()
        self.mock_list.postProcess.return_value = []

    async def test_blank(self):
        self.mock_split.return_value = []
        self.assertEqual(
            await library.create_messages(self.command, self.args), [''])
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'textconvert')
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.assertFalse(self.mock_convert.called)
        self.assertFalse(self.mock_format.called)

    async def test_plain(self):
        self.mock_split.return_value = [
            CustomFieldParts('Kappa', None, None, None, None, None, None, None)
            ]
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['Kappa'])
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'textconvert')
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.assertFalse(self.mock_convert.called)
        self.assertFalse(self.mock_format.called)

    async def test_field(self):
        self.mock_split.return_value = [
            CustomFieldParts('', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default', 'original')
            ]
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['default'])
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'textconvert')
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.mock_convert.assert_called_once_with(TypeMatch(CustomFieldArgs))
        self.mock_format.assert_called_once_with('default', 'format', False)

    async def test_plain_plain(self):
        """
        In practice this should not be a scenario but just support it
        anyways
        """
        self.mock_split.return_value = [
            CustomFieldParts('KappaRoss', None, None, None, None, None, None,
                             None),
            CustomFieldParts(' KappaPride', None, None, None, None, None, None,
                             None),
            ]
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['KappaRoss KappaPride'])
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'textconvert')
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.assertFalse(self.mock_convert.called)
        self.assertFalse(self.mock_format.called)

    async def test_plain_field(self):
        self.mock_split.return_value = [
            CustomFieldParts('Kappa ', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default', 'original')
            ]
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['Kappa default'])
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'textconvert')
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.mock_convert.assert_called_once_with(TypeMatch(CustomFieldArgs))
        self.mock_format.assert_called_once_with('default', 'format', False)

    async def test_field_field(self):
        self.mock_split.return_value = [
            CustomFieldParts('', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default1', 'original'),
            CustomFieldParts('', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default2', 'original'),
            ]
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['default1default2'])
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'textconvert')
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.mock_convert.assert_has_calls(
            [call(TypeMatch(CustomFieldArgs))] * 2)
        self.assertEqual(self.mock_format.call_args_list,
                         [call('default1', 'format', False),
                          call('default2', 'format', False)])

    async def test_field_plain(self):
        self.mock_split.return_value = [
            CustomFieldParts('', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default', 'original'),
            CustomFieldParts(' Kappa', None, None, None, None, None, None,
                             None)
            ]
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['default Kappa'])
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'textconvert')
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.mock_convert.assert_called_once_with(TypeMatch(CustomFieldArgs))
        self.mock_format.assert_called_once_with('default', 'format', False)

    async def test_plain_field_plain(self):
        self.mock_split.return_value = [
            CustomFieldParts('Kappa ', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default', 'original'),
            CustomFieldParts(' Kappa', None, None, None, None, None, None,
                             None)
            ]
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['Kappa default Kappa'])
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'textconvert')
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.mock_convert.assert_called_once_with(TypeMatch(CustomFieldArgs))
        self.mock_format.assert_called_once_with('default', 'format', False)

    async def test_plain_field_field(self):
        self.mock_split.return_value = [
            CustomFieldParts('Kappa ', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default1', 'original'),
            CustomFieldParts('', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default2', 'original'),
            ]
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['Kappa default1default2'])
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'textconvert')
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.mock_convert.assert_has_calls(
            [call(TypeMatch(CustomFieldArgs))] * 2)
        self.assertEqual(self.mock_format.call_args_list,
                         [call('default1', 'format', False),
                          call('default2', 'format', False)])

    async def test_field_plain_field(self):
        self.mock_split.return_value = [
            CustomFieldParts('', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default1', 'original'),
            CustomFieldParts(' Kappa ', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default2', 'original'),
            ]
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['default1 Kappa default2'])
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'textconvert')
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.mock_convert.assert_has_calls(
            [call(TypeMatch(CustomFieldArgs))] * 2)
        self.assertEqual(self.mock_format.call_args_list,
                         [call('default1', 'format', False),
                          call('default2', 'format', False)])

    async def test_field_field_plain(self):
        self.mock_split.return_value = [
            CustomFieldParts('', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default1', 'original'),
            CustomFieldParts('', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default2', 'original'),
            CustomFieldParts(' Kappa', None, None, None, None, None, None,
                             None)
            ]
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['default1default2 Kappa'])
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'textconvert')
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.mock_convert.assert_has_calls(
            [call(TypeMatch(CustomFieldArgs))] * 2)
        self.assertEqual(self.mock_format.call_args_list,
                         [call('default1', 'format', False),
                          call('default2', 'format', False)])

    async def test_split_except(self):
        self.mock_split.side_effect = ValueError
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['Kappa KappaRoss KappaPride'])
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.assertFalse(self.mock_convert.called)
        self.assertFalse(self.mock_format.called)

    async def test_convert_except(self):
        self.mock_convert.side_effect = Exception
        self.mock_split.return_value = [
            CustomFieldParts('Kappa ', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default', 'original')
            ]
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['Kappa original'])
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.mock_convert.assert_called_once_with(TypeMatch(CustomFieldArgs))
        self.assertFalse(self.mock_format.called)

    async def test_format_except(self):
        self.mock_format.side_effect = Exception
        self.mock_split.return_value = [
            CustomFieldParts('Kappa ', 'field', 'format', 'prefix', 'suffix',
                             'param', 'default', 'original')
            ]
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['Kappa original'])
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.mock_convert.assert_called_once_with(TypeMatch(CustomFieldArgs))
        self.mock_format.assert_called_once_with('default', 'format', False)

    async def test_post_process(self):
        async def process(args):
            args.messages[0] = 'Kappa'
        mock_process = CoroutineMock(spec=process, side_effect=process)
        self.mock_list.postProcess.return_value = [mock_process]
        self.mock_split.return_value = []
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['Kappa'])
        mock_process.assert_called_once_with(TypeMatch(CustomProcessArgs))

    async def test_split_except_post_process(self):
        async def process(args):
            args.messages[0] = 'Kappa'
        mock_process = CoroutineMock(spec=process, side_effect=process)
        self.mock_list.postProcess = [mock_process]
        self.mock_split.side_effect = ValueError
        self.assertEqual(
            await library.create_messages(self.command, self.args),
            ['Kappa KappaRoss KappaPride'])
        self.mock_split.assert_called_once_with('Kappa KappaRoss KappaPride')
        self.assertFalse(self.mock_convert.called)
        self.assertFalse(self.mock_format.called)
        self.assertFalse(mock_process.called)


class TestCustomCommandLibraryCustomGetActionCommand(unittest.TestCase):
    def test(self):
        message = Message('')
        self.assertIsNone(library.parse_action_message(message, 'botgotsthis'))

    def test_1_arg(self):
        message = Message('!command')
        self.assertIsNone(library.parse_action_message(message, 'botgotsthis'))

    def test_2_args(self):
        message = Message('!command list')
        self.assertIsNone(library.parse_action_message(message, 'botgotsthis'))

    def test_3_args(self):
        message = Message('!command add Kappa')
        self.assertEqual(
            library.parse_action_message(message, 'botgotsthis'),
            CommandActionTokens('add', 'botgotsthis', '', 'Kappa', ''))

    def test_4_args(self):
        message = Message('!command add Kappa PogChamp')
        self.assertEqual(
            library.parse_action_message(message, 'botgotsthis'),
            CommandActionTokens('add', 'botgotsthis', '', 'Kappa', 'PogChamp'))

    def test_5_args(self):
        message = Message('!command add Kappa PogChamp  KreyGasm')
        self.assertEqual(
            library.parse_action_message(message, 'botgotsthis'),
            CommandActionTokens('add', 'botgotsthis', '', 'Kappa',
                                'PogChamp  KreyGasm'))

    def test_wrong_level(self):
        message = Message('!command level=owner')
        self.assertIsNone(library.parse_action_message(message, 'botgotsthis'))

    def test_wrong_level_2_args(self):
        message = Message('!command level=owner add')
        self.assertEqual(
            library.parse_action_message(message, 'botgotsthis'),
            CommandActionTokens('level=owner', 'botgotsthis', '', 'add', ''))

    def test_level_2_args(self):
        message = Message('!command add level=owner')
        self.assertIsNone(library.parse_action_message(message, 'botgotsthis'))

    def test_level_3_args(self):
        message = Message('!command add level=owner Kappa')
        self.assertEqual(
            library.parse_action_message(message, 'botgotsthis'),
            CommandActionTokens('add', 'botgotsthis', 'owner', 'Kappa', ''))

    def test_level_4_args(self):
        message = Message('!command add level=owner Kappa PogChamp')
        self.assertEqual(
            library.parse_action_message(message, 'botgotsthis'),
            CommandActionTokens('add', 'botgotsthis', 'owner', 'Kappa',
                                'PogChamp'))

    def test_level_5_args(self):
        message = Message('!command add level=owner Kappa PogChamp  KreyGasm')
        self.assertEqual(
            library.parse_action_message(message, 'botgotsthis'),
            CommandActionTokens('add', 'botgotsthis', 'owner', 'Kappa',
                                'PogChamp  KreyGasm'))

    def test_level_unknown(self):
        message = Message('!command add level=abc Kappa')
        self.assertEqual(
            library.parse_action_message(message, 'botgotsthis'),
            CommandActionTokens('add', 'botgotsthis', None, 'Kappa', ''))

    def test_level_blank(self):
        for level in ['', 'any', 'ANY', 'all', 'public']:
            message = Message('!command add level=%s Kappa' % level)
            self.assertEqual(
                library.parse_action_message(message, 'botgotsthis'),
                CommandActionTokens('add', 'botgotsthis', '', 'Kappa', ''),
                level)

    def test_level_subcriber(self):
        for level in ['subscriber', 'sub']:
            message = Message('!command add level=%s Kappa' % level)
            self.assertEqual(
                library.parse_action_message(message, 'botgotsthis'),
                CommandActionTokens('add', 'botgotsthis', 'subscriber',
                                    'Kappa', ''),
                level)

    def test_level_moderator(self):
        for level in ['moderator', 'mod']:
            message = Message('!command add level=%s Kappa' % level)
            self.assertEqual(
                library.parse_action_message(message, 'botgotsthis'),
                CommandActionTokens('add', 'botgotsthis', 'moderator',
                                    'Kappa', ''),
                level)

    def test_level_broadcaster(self):
        for level in ['broadcaster', 'streamer', 'me']:
            message = Message('!command add level=%s Kappa' % level)
            self.assertEqual(
                library.parse_action_message(message, 'botgotsthis'),
                CommandActionTokens('add', 'botgotsthis', 'broadcaster',
                                    'Kappa', ''),
                level)

    def test_level_global_moderator(self):
        for level in ['globalmod', 'globalMod', 'global_mod', 'gmod']:
            message = Message('!command add level=%s Kappa' % level)
            self.assertEqual(
                library.parse_action_message(message, 'botgotsthis'),
                CommandActionTokens('add', 'botgotsthis', 'globalMod',
                                    'Kappa', ''),
                level)

    def test_level_admin(self):
        for level in ['admin', 'twitchadmin']:
            message = Message('!command add level=%s Kappa' % level)
            self.assertEqual(
                library.parse_action_message(message, 'botgotsthis'),
                CommandActionTokens('add', 'botgotsthis', 'admin', 'Kappa',
                                    ''),
                level)

    def test_level_staff(self):
        for level in ['staff', 'twitchstaff']:
            message = Message('!command add level=%s Kappa' % level)
            self.assertEqual(
                library.parse_action_message(message, 'botgotsthis'),
                CommandActionTokens('add', 'botgotsthis', 'staff', 'Kappa',
                                    ''),
                level)

    def test_level_owner(self):
        for level in ['owner', 'self', 'bot']:
            message = Message('!command add level=%s Kappa' % level)
            self.assertEqual(
                library.parse_action_message(message, 'botgotsthis'),
                CommandActionTokens('add', 'botgotsthis', 'owner', 'Kappa',
                                    ''),
                level)


class TestCustomCommandLibraryCustomSplitMessage(unittest.TestCase):
    def test(self):
        self.assertEqual(library.split_message(''), [])

    def test_plain(self):
        self.assertEqual(
            library.split_message('Kappa'),
            [CustomFieldParts('Kappa', None, None, None, None, None, None,
                              None)])
        self.assertEqual(
            library.split_message('Kappa KappaPride KappaRoss'),
            [CustomFieldParts('Kappa KappaPride KappaRoss', None, None, None,
                              None, None, None, None)])

    def test_field(self):
        self.assertEqual(
            library.split_message('{field}'),
            [CustomFieldParts('', 'field', None, None, None, None, None,
                              '{field}')])

    def test_field_format(self):
        self.assertEqual(
            library.split_message('{field:ascii}'),
            [CustomFieldParts('', 'field', 'ascii', None, None, None, None,
                              '{field:ascii}')])

    def test_field_prefix(self):
        self.assertEqual(
            library.split_message('{field<prefix }'),
            [CustomFieldParts('', 'field', None, 'prefix ', None, None, None,
                              '{field<prefix }')])

    def test_field_suffix(self):
        self.assertEqual(
            library.split_message('{field> suffix}'),
            [CustomFieldParts('', 'field', None, None, ' suffix', None, None,
                              '{field> suffix}')])

    def test_field_param(self):
        self.assertEqual(
            library.split_message('{field@param}'),
            [CustomFieldParts('', 'field', None, None, None, 'param', None,
                              '{field@param}')])

    def test_field_default(self):
        self.assertEqual(
            library.split_message('{field!default}'),
            [CustomFieldParts('', 'field', None, None, None, None, 'default',
                              '{field!default}')])

    def test_field_prefix_suffix(self):
        self.assertEqual(
            library.split_message('{field<prefix>suffix}'),
            [CustomFieldParts('', 'field', None, 'prefix', 'suffix', None,
                              None, '{field<prefix>suffix}')])

    def test_field_format_default(self):
        self.assertEqual(
            library.split_message('{field:format!default}'),
            [CustomFieldParts('', 'field', 'format', None, None, None,
                              'default', '{field:format!default}')])

    def test_field_format_prefix_suffix_param_default(self):
        self.assertEqual(
            library.split_message(
                '{field:format<prefix>suffix@param!default}'),
            [CustomFieldParts('', 'field', 'format', 'prefix', 'suffix',
                              'param', 'default',
                              '{field:format<prefix>suffix@param!default}')])

    def test_field_blank(self):
        self.assertEqual(
            library.split_message('{}'),
            [CustomFieldParts('', '', None, None, None, None, None, '{}')])

    def test_field_format_prefix_suffix_param_default_all_blank(self):
        self.assertEqual(
            library.split_message('{:<>@!}'),
            [CustomFieldParts('', '', '', '', '', '', '', '{:<>@!}')])

    def test_plain_field(self):
        self.assertEqual(
            library.split_message('Kappa{}'),
            [CustomFieldParts('Kappa', '', None, None, None, None, None,
                              '{}')])

    def test_field_plain(self):
        self.assertEqual(
            library.split_message('{}Kappa'),
            [CustomFieldParts('', '', None, None, None, None, None, '{}'),
             CustomFieldParts('Kappa', None, None, None, None, None, None,
                              None),
             ])

    def test_field_field(self):
        self.assertEqual(
            library.split_message('{}{}'),
            [CustomFieldParts('', '', None, None, None, None, None, '{}'),
             CustomFieldParts('', '', None, None, None, None, None, '{}'),
             ])

    def test_plain_field_plain_field_plain(self):
        self.assertEqual(
            library.split_message('Kappa{}Kappa{}Kappa'),
            [CustomFieldParts('Kappa', '', None, None, None, None, None, '{}'),
             CustomFieldParts('Kappa', '', None, None, None, None, None, '{}'),
             CustomFieldParts('Kappa', None, None, None, None, None, None,
                              None),
             ])

    def test_plain_escape(self):
        self.assertEqual(
            library.split_message('{{'),
            [CustomFieldParts('{', None, None, None, None, None, None, None)])
        self.assertEqual(
            library.split_message('}}'),
            [CustomFieldParts('}', None, None, None, None, None, None, None)])

    def test_field_escape(self):
        """Fields cannot start with { since {{{ will read the escape first"""
        self.assertEqual(
            library.split_message('{ {{}'),
            [CustomFieldParts('', ' {', None, None, None, None, None,
                              '{ {{}')])
        self.assertEqual(
            library.split_message('{}}}'),
            [CustomFieldParts('', '}', None, None, None, None, None,
                              '{}}}')])
        self.assertEqual(
            library.split_message('{::}'),
            [CustomFieldParts('', ':', None, None, None, None, None,
                              '{::}')])
        self.assertEqual(
            library.split_message('{<<}'),
            [CustomFieldParts('', '<', None, None, None, None, None,
                              '{<<}')])
        self.assertEqual(
            library.split_message('{>>}'),
            [CustomFieldParts('', '>', None, None, None, None, None,
                              '{>>}')])
        self.assertEqual(
            library.split_message('{@@}'),
            [CustomFieldParts('', '@', None, None, None, None, None,
                              '{@@}')])
        self.assertEqual(
            library.split_message('{!!}'),
            [CustomFieldParts('', '!', None, None, None, None, None,
                              '{!!}')])

    def test_format_escape(self):
        self.assertEqual(
            library.split_message('{:{{}'),
            [CustomFieldParts('', '', '{', None, None, None, None,
                              '{:{{}')])
        self.assertEqual(
            library.split_message('{:}}}'),
            [CustomFieldParts('', '', '}', None, None, None, None,
                              '{:}}}')])
        self.assertEqual(
            library.split_message('{: ::}'),
            [CustomFieldParts('', '', ' ::', None, None, None, None,
                              '{: ::}')])
        self.assertEqual(
            library.split_message('{:<<}'),
            [CustomFieldParts('', '', '<', None, None, None, None,
                              '{:<<}')])
        self.assertEqual(
            library.split_message('{:>>}'),
            [CustomFieldParts('', '', '>', None, None, None, None,
                              '{:>>}')])
        self.assertEqual(
            library.split_message('{:@@}'),
            [CustomFieldParts('', '', '@', None, None, None, None,
                              '{:@@}')])
        self.assertEqual(
            library.split_message('{:!!}'),
            [CustomFieldParts('', '', '!', None, None, None, None,
                              '{:!!}')])

    def test_prefix_escape(self):
        self.assertEqual(
            library.split_message('{<{{}'),
            [CustomFieldParts('', '', None, '{', None, None, None,
                              '{<{{}')])
        self.assertEqual(
            library.split_message('{<}}}'),
            [CustomFieldParts('', '', None, '}', None, None, None,
                              '{<}}}')])
        self.assertEqual(
            library.split_message('{<:}'),
            [CustomFieldParts('', '', None, ':', None, None, None,
                              '{<:}')])
        self.assertEqual(
            library.split_message('{< <<}'),
            [CustomFieldParts('', '', None, ' <<', None, None, None,
                              '{< <<}')])
        self.assertEqual(
            library.split_message('{<>>}'),
            [CustomFieldParts('', '', None, '>', None, None, None,
                              '{<>>}')])
        self.assertEqual(
            library.split_message('{<@@}'),
            [CustomFieldParts('', '', None, '@', None, None, None,
                              '{<@@}')])
        self.assertEqual(
            library.split_message('{<!!}'),
            [CustomFieldParts('', '', None, '!', None, None, None,
                              '{<!!}')])

    def test_suffix_escape(self):
        self.assertEqual(
            library.split_message('{>{{}'),
            [CustomFieldParts('', '', None, None, '{', None, None,
                              '{>{{}')])
        self.assertEqual(
            library.split_message('{>}}}'),
            [CustomFieldParts('', '', None, None, '}', None, None,
                              '{>}}}')])
        self.assertEqual(
            library.split_message('{>:}'),
            [CustomFieldParts('', '', None, None, ':', None, None,
                              '{>:}')])
        self.assertEqual(
            library.split_message('{><}'),
            [CustomFieldParts('', '', None, None, '<', None, None,
                              '{><}')])
        self.assertEqual(
            library.split_message('{> >>}'),
            [CustomFieldParts('', '', None, None, ' >>', None, None,
                              '{> >>}')])
        self.assertEqual(
            library.split_message('{>@@}'),
            [CustomFieldParts('', '', None, None, '@', None, None,
                              '{>@@}')])
        self.assertEqual(
            library.split_message('{>!!}'),
            [CustomFieldParts('', '', None, None, '!', None, None,
                              '{>!!}')])

    def test_param_escape(self):
        self.assertEqual(
            library.split_message('{@{{}'),
            [CustomFieldParts('', '', None, None, None, '{', None,
                              '{@{{}')])
        self.assertEqual(
            library.split_message('{@}}}'),
            [CustomFieldParts('', '', None, None, None, '}', None,
                              '{@}}}')])
        self.assertEqual(
            library.split_message('{@:}'),
            [CustomFieldParts('', '', None, None, None, ':', None,
                              '{@:}')])
        self.assertEqual(
            library.split_message('{@<}'),
            [CustomFieldParts('', '', None, None, None, '<', None,
                              '{@<}')])
        self.assertEqual(
            library.split_message('{@>}'),
            [CustomFieldParts('', '', None, None, None, '>', None,
                              '{@>}')])
        self.assertEqual(
            library.split_message('{@ @@}'),
            [CustomFieldParts('', '', None, None, None, ' @@', None,
                              '{@ @@}')])
        self.assertEqual(
            library.split_message('{@!!}'),
            [CustomFieldParts('', '', None, None, None, '!', None,
                              '{@!!}')])

    def test_default_escape(self):
        self.assertEqual(
            library.split_message('{!{{}'),
            [CustomFieldParts('', '', None, None, None, None, '{',
                              '{!{{}')])
        self.assertEqual(
            library.split_message('{!}}}'),
            [CustomFieldParts('', '', None, None, None, None, '}',
                              '{!}}}')])
        self.assertEqual(
            library.split_message('{!:}'),
            [CustomFieldParts('', '', None, None, None, None, ':',
                              '{!:}')])
        self.assertEqual(
            library.split_message('{!<}'),
            [CustomFieldParts('', '', None, None, None, None, '<',
                              '{!<}')])
        self.assertEqual(
            library.split_message('{!>}'),
            [CustomFieldParts('', '', None, None, None, None, '>',
                              '{!>}')])
        self.assertEqual(
            library.split_message('{!@}'),
            [CustomFieldParts('', '', None, None, None, None, '@',
                              '{!@}')])
        self.assertEqual(
            library.split_message('{! !!}'),
            [CustomFieldParts('', '', None, None, None, None, ' !!',
                              '{! !!}')])

    def test_multiple_escape(self):
        self.assertEqual(
            library.split_message('{{{:::<<<>>>@@@!!!}}}'),
            [CustomFieldParts('{', ':', '<', '>', '@', '!', '}',
                              '{:::<<<>>>@@@!!!}}}')])
        self.assertEqual(
            library.split_message('{{{{:<>@!}}}}'),
            [CustomFieldParts('{{:<>@!}}',
                              None, None, None, None, None, None, None)])

    def test_unpaired_brace(self):
        self.assertRaises(ValueError, library.split_message, '{')
        self.assertRaises(ValueError, library.split_message, '}')
        self.assertRaises(ValueError, library.split_message, '{ {}')
        self.assertRaises(ValueError, library.split_message, '{:{}')
        self.assertRaises(ValueError, library.split_message, '{<{}')
        self.assertRaises(ValueError, library.split_message, '{>{}')
        self.assertRaises(ValueError, library.split_message, '{@{}')
        self.assertRaises(ValueError, library.split_message, '{!{}')
        self.assertRaises(ValueError, library.split_message, '{}}')
        self.assertRaises(ValueError, library.split_message, '{:}}')
        self.assertRaises(ValueError, library.split_message, '{<}}')
        self.assertRaises(ValueError, library.split_message, '{>}}')
        self.assertRaises(ValueError, library.split_message, '{@}}')
        self.assertRaises(ValueError, library.split_message, '{!}}')


class TestCustomCommandLibraryCustomConvertField(asynctest.TestCase):
    def setUp(self):
        self.args = CustomFieldArgs('', None, None, None, None, Message(''),
                                    Mock(spec=Channel), 'botgotsthis',
                                    Mock(spec=ChatPermissionSet),
                                    datetime(2000, 1, 1))

        patcher = patch('lib.items.custom', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_list = patcher.start()
        self.mock_list.fields.return_value = []

    async def test_no_fields(self):
        self.assertIsNone(await library.convert_field(self.args))

    async def test_none(self):
        async def convert(args):
            pass
        mock_convert = CoroutineMock(spec=convert, return_value=None)
        self.mock_list.fields.return_value = [mock_convert]
        self.assertIsNone(await library.convert_field(self.args))
        self.assertEqual(mock_convert.call_count, 1)

    async def test(self):
        async def convert(args):
            pass
        mock_convert = CoroutineMock(spec=convert, return_value='Kappa')
        self.mock_list.fields.return_value = [mock_convert]
        self.assertEqual(await library.convert_field(self.args), 'Kappa')
        self.assertEqual(mock_convert.call_count, 1)


class TestCustomCommandLibraryCustomFormat(unittest.TestCase):
    def setUp(self):
        patcher = patch('lib.helper.textformat.format', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_format = patcher.start()

    def test_no_format(self):
        self.assertEqual(library.format('Kappa', 'test', False), 'Kappa')
        self.assertFalse(self.mock_format.called)

    def test_none_format(self):
        self.assertEqual(library.format('Kappa', None, False), 'Kappa')
        self.assertFalse(self.mock_format.called)

    def test_with_format(self):
        self.mock_format.return_value = 'Keepo'
        self.assertEqual(library.format('Kappa', 'test', True), 'Keepo')
        self.mock_format.assert_called_once_with('Kappa', 'test')
