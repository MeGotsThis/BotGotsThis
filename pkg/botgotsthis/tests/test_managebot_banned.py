import asynctest

from asynctest.mock import MagicMock, Mock, patch

from lib.database import DatabaseMain
from lib.data.message import Message
from tests.unittest.base_managebot import TestManageBot, send
from tests.unittest.mock_class import StrContains, AsyncIterator

# Needs to be imported last
from ..manage import banned


class TestManageBotBanned(TestManageBot):
    def setUp(self):
        super().setUp()
        self.database.isChannelBannedReason.return_value = None

    async def test_false(self):
        self.assertIs(await banned.manageBanned(self.args), False)
        args = self.args._replace(message=Message('!managebot'))
        self.assertIs(await banned.manageBanned(args), False)
        args = self.args._replace(message=Message('!managebot banned'))
        self.assertIs(await banned.manageBanned(args), False)
        message = Message('!managebot banned no_action')
        args = self.args._replace(message=message)
        self.assertIs(await banned.manageBanned(args), False)
        self.assertFalse(self.database.isChannelBannedReason.called)
        message = Message('!managebot banned no_action some_channel no_arg')
        args = self.args._replace(message=message)
        self.assertIs(await banned.manageBanned(args), False)
        self.assertFalse(self.send.called)

    async def test_need_reason(self):
        message = Message('!managebot banned add botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await banned.manageBanned(args), True)
        self.send.assert_called_once_with(
            StrContains(self.args.nick, 'Reason', 'specif'))

    @patch(banned.__name__ + '.list_banned_channels')
    async def test_list(self, mock_list):
        mock_list.return_value = True
        message = Message('!managebot banned list')
        args = self.args._replace(message=message)
        self.assertIs(await banned.manageBanned(args), True)
        mock_list.assert_called_once_with(self.send)

    @patch(banned.__name__ + '.insert_banned_channel')
    async def test_add(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot banned add botgotsthis Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await banned.manageBanned(args), True)
        mock_add.assert_called_once_with(
            'botgotsthis', 'Kappa', 'botgotsthis', self.send)

    @patch(banned.__name__ + '.insert_banned_channel')
    async def test_insert(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot banned insert botgotsthis Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await banned.manageBanned(args), True)
        mock_add.assert_called_once_with(
            'botgotsthis', 'Kappa', 'botgotsthis', self.send)

    @patch(banned.__name__ + '.delete_banned_channel')
    async def test_delete(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot banned delete botgotsthis Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await banned.manageBanned(args), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', 'Kappa', 'botgotsthis', self.send)

    @patch(banned.__name__ + '.delete_banned_channel')
    async def test_del(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot banned del botgotsthis Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await banned.manageBanned(args), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', 'Kappa', 'botgotsthis', self.send)

    @patch(banned.__name__ + '.delete_banned_channel')
    async def test_remove(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot banned remove botgotsthis Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await banned.manageBanned(args), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', 'Kappa', 'botgotsthis', self.send)

    @patch(banned.__name__ + '.delete_banned_channel')
    async def test_rem(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot banned rem botgotsthis Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await banned.manageBanned(args), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', 'Kappa', 'botgotsthis', self.send)


class TestManageBotBannedListBannedChannels(asynctest.TestCase):
    def setUp(self):
        self.database = MagicMock(spec=DatabaseMain)
        self.database.__aenter__.return_value = self.database
        self.database.__aexit__.return_value = False
        self.send = Mock(spec=send)

        patcher = patch('lib.database.get_main_database')
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database

    async def test(self):
        self.database.listBannedChannels.return_value = AsyncIterator([])
        self.assertIs(
            await banned.list_banned_channels(self.send), True)
        self.send.assert_called_once_with(StrContains('no'))

    @patch('lib.helper.message.messagesFromItems', autospec=True)
    async def test_one(self, mock_messages):
        self.database.listBannedChannels.return_value = AsyncIterator(
            ['botgotsthis'])
        mock_messages.return_value = ''
        self.assertIs(
            await banned.list_banned_channels(self.send), True)
        mock_messages.assert_called_once_with(['botgotsthis'],
                                              StrContains('Banned'))
        self.send.assert_called_once_with('')

    @patch('lib.helper.message.messagesFromItems', autospec=True)
    async def test_many(self, mock_messages):
        self.database.listBannedChannels.return_value = AsyncIterator(
            ['botgotsthis', 'megotsthis'])
        mock_messages.return_value = ''
        self.assertIs(
            await banned.list_banned_channels(self.send), True)
        mock_messages.assert_called_once_with(['botgotsthis', 'megotsthis'],
                                              StrContains('Banned'))
        self.send.assert_called_once_with('')


class TestManageBotBannedInsertBannedChannel(asynctest.TestCase):
    def setUp(self):
        self.database = MagicMock(spec=DatabaseMain)
        self.database.__aenter__.return_value = self.database
        self.database.__aexit__.return_value = False
        self.send = Mock(spec=send)

        patcher = patch('bot.utils.partChannel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_part = patcher.start()

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.botnick = 'botgotsthis'

        patcher = patch('lib.database.get_main_database')
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database

    async def test(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.addBannedChannel.return_value = True
        self.assertIs(
            await banned.insert_banned_channel(
                'megotsthis', 'Kappa', 'botgotsthis', self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.database.addBannedChannel.assert_called_once_with(
            'megotsthis', 'Kappa', 'botgotsthis')
        self.database.discardAutoJoin.assert_called_once_with('megotsthis')
        self.mock_part.assert_called_once_with('megotsthis')
        self.send.assert_called_once_with(StrContains('megotsthis', 'ban'))

    async def test_banned(self):
        self.database.isChannelBannedReason.return_value = 'DansGame'
        self.assertIs(
            await banned.insert_banned_channel(
                'megotsthis', 'Kappa', 'botgotsthis', self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.assertFalse(self.database.addBannedChannel.called)
        self.assertFalse(self.database.discardAutoJoin.called)
        self.assertFalse(self.mock_part.called)
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'ban', 'DansGame'))

    async def test_banned_blank(self):
        self.database.isChannelBannedReason.return_value = ''
        self.assertIs(
            await banned.insert_banned_channel(
                'megotsthis', 'Kappa', 'botgotsthis', self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.assertFalse(self.database.addBannedChannel.called)
        self.assertFalse(self.database.discardAutoJoin.called)
        self.assertFalse(self.mock_part.called)
        self.send.assert_called_once_with(StrContains('megotsthis', 'ban'))

    async def test_database_error(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.addBannedChannel.return_value = False
        self.assertIs(
            await banned.insert_banned_channel(
                'megotsthis', 'Kappa', 'botgotsthis', self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.database.addBannedChannel.assert_called_once_with(
            'megotsthis', 'Kappa', 'botgotsthis')
        self.assertFalse(self.database.discardAutoJoin.called)
        self.assertFalse(self.mock_part.called)
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'not', 'ban'))

    async def test_bot(self):
        self.database.isChannelBannedReason.return_value = 'Kappa'
        self.assertIs(
            await banned.insert_banned_channel(
                'botgotsthis', 'Kappa', 'botgotsthis', self.send),
            True)
        self.assertFalse(self.database.isChannelBannedReason.called)
        self.assertFalse(self.database.addBannedChannel.called)
        self.assertFalse(self.database.discardAutoJoin.called)
        self.assertFalse(self.mock_part.called)
        self.send.assert_called_once_with(StrContains('not', 'ban', 'bot'))


class TestManageBotBannedDeleteBannedChannel(asynctest.TestCase):
    def setUp(self):
        self.database = MagicMock(spec=DatabaseMain)
        self.database.__aenter__.return_value = self.database
        self.database.__aexit__.return_value = False
        self.send = Mock(spec=send)

        patcher = patch('lib.database.get_main_database')
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database

    async def test(self):
        self.database.isChannelBannedReason.return_value = 'Kappa'
        self.database.removeBannedChannel.return_value = True
        self.assertIs(
            await banned.delete_banned_channel(
                'megotsthis', 'Kappa', 'botgotsthis', self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.database.removeBannedChannel.assert_called_once_with(
            'megotsthis', 'Kappa', 'botgotsthis')
        self.send.assert_called_once_with(StrContains('megotsthis', 'unban'))

    async def test_blank(self):
        self.database.isChannelBannedReason.return_value = ''
        self.database.removeBannedChannel.return_value = True
        self.assertIs(
            await banned.delete_banned_channel(
                'megotsthis', 'Kappa', 'botgotsthis', self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.database.removeBannedChannel.assert_called_once_with(
            'megotsthis', 'Kappa', 'botgotsthis')
        self.send.assert_called_once_with(StrContains('megotsthis', 'unban'))

    async def test_not_banned(self):
        self.database.isChannelBannedReason.return_value = None
        self.assertIs(
            await banned.delete_banned_channel(
                'megotsthis', 'Kappa', 'botgotsthis', self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.assertFalse(self.database.removeBannedChannel.called)
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'not', 'ban'))

    async def test_database_error(self):
        self.database.isChannelBannedReason.return_value = 'Kappa'
        self.database.removeBannedChannel.return_value = False
        self.assertIs(
            await banned.delete_banned_channel(
                'megotsthis', 'Kappa', 'botgotsthis', self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.database.removeBannedChannel.assert_called_once_with(
            'megotsthis', 'Kappa', 'botgotsthis')
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'not', 'unban'))
