import asynctest

from datetime import datetime
from io import StringIO

from asynctest.mock import MagicMock, Mock, patch

from lib.database import DatabaseMain
from lib.data import AutoJoinChannel
from lib.data.message import Message
from tests.unittest.base_managebot import TestManageBot, send
from tests.unittest.mock_class import AsyncIterator, StrContains

# Needs to be imported last
from ...channel import library
from ..manage import autojoin


class TestManageBotAutoJoin(TestManageBot):
    def setUp(self):
        super().setUp()
        self.database.isChannelBannedReason.return_value = None

    async def test_false(self):
        self.assertIs(await autojoin.manageAutoJoin(self.args), False)
        args = self.args._replace(message=Message('!managebot'))
        self.assertIs(await autojoin.manageAutoJoin(args), False)
        args = self.args._replace(message=Message('!managebot autojoin'))
        self.assertIs(await autojoin.manageAutoJoin(args), False)
        message = Message('!managebot autojoin no_action')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), False)
        self.assertFalse(self.database.isChannelBannedReason.called)
        message = Message('!managebot autojoin no_action no_arg')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), False)
        self.assertFalse(self.send.called)
        self.database.isChannelBannedReason.assert_called_with('no_arg')

    @patch(autojoin.__name__ + '.reload_server')
    async def test_banned_channel(self, mock_reload):
        self.database.isChannelBannedReason.return_value = 'Reason'
        mock_reload.return_value = True
        message = Message('!managebot autojoin action banned_channel')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        self.send.assert_called_once_with(StrContains('banned_channel', 'ban'))

    @patch(autojoin.__name__ + '.reload_server')
    async def test_banned_channel_blank(self, mock_reload):
        self.database.isChannelBannedReason.return_value = ''
        mock_reload.return_value = True
        message = Message('!managebot autojoin action banned_channel')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        self.send.assert_called_once_with(StrContains('banned_channel', 'ban'))

    @patch(autojoin.__name__ + '.reload_server')
    async def test_reloadserver(self, mock_reload):
        mock_reload.return_value = True
        message = Message('!managebot autojoin reloadserver')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_reload.assert_called_once_with(self.send)

    @patch(library.__name__ + '.auto_join_add')
    async def test_add(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot autojoin add botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_add.assert_called_once_with(self.database, 'botgotsthis',
                                         self.send)

    @patch(library.__name__ + '.auto_join_add')
    async def test_insert(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot autojoin insert botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_add.assert_called_once_with(self.database, 'botgotsthis',
                                         self.send)

    @patch(library.__name__ + '.auto_join_add')
    async def test_join(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot autojoin join botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_add.assert_called_once_with(self.database, 'botgotsthis',
                                         self.send)

    @patch(library.__name__ + '.auto_join_delete')
    async def test_delete(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin delete botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_delete.assert_called_once_with(self.database, 'botgotsthis',
                                            self.send)

    @patch(library.__name__ + '.auto_join_delete')
    async def test_del(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin del botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_delete.assert_called_once_with(self.database, 'botgotsthis',
                                            self.send)

    @patch(library.__name__ + '.auto_join_delete')
    async def test_remove(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin remove botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_delete.assert_called_once_with(self.database, 'botgotsthis',
                                            self.send)

    @patch(library.__name__ + '.auto_join_delete')
    async def test_rem(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin rem botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_delete.assert_called_once_with(self.database, 'botgotsthis',
                                            self.send)

    @patch(library.__name__ + '.auto_join_delete')
    async def test_part(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin part botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_delete.assert_called_once_with(self.database, 'botgotsthis',
                                            self.send)

    @patch(autojoin.__name__ + '.auto_join_priority')
    async def test_priority(self, mock_priority):
        mock_priority.return_value = True
        message = Message('!managebot autojoin priority botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_priority.assert_called_once_with('botgotsthis', 0, self.send)

    @patch(autojoin.__name__ + '.auto_join_priority')
    async def test_pri(self, mock_priority):
        mock_priority.return_value = True
        message = Message('!managebot autojoin pri botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_priority.assert_called_once_with('botgotsthis', 0, self.send)

    @patch(autojoin.__name__ + '.auto_join_priority')
    async def test_priority_gibberish(self, mock_priority):
        mock_priority.return_value = True
        message = Message('!managebot autojoin priority botgotsthis abc')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_priority.assert_called_once_with('botgotsthis', 0, self.send)

    @patch(autojoin.__name__ + '.auto_join_priority')
    async def test_priority_integer(self, mock_priority):
        mock_priority.return_value = True
        message = Message('!managebot autojoin priority botgotsthis 1')
        args = self.args._replace(message=message)
        self.assertIs(await autojoin.manageAutoJoin(args), True)
        mock_priority.assert_called_once_with('botgotsthis', 1, self.send)


class TestManageBotAutoJoinAutoJoinPriority(asynctest.TestCase):
    def setUp(self):
        self.database = MagicMock(spec=DatabaseMain)
        self.database.__aenter__.return_value = self.database
        self.database.__aexit__.return_value = False
        self.send = Mock(spec=send)

        patcher = patch.object(DatabaseMain, 'acquire')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database

    async def test(self):
        self.database.setAutoJoinPriority.return_value = True
        self.assertIs(
            await autojoin.auto_join_priority('botgotsthis', 0, self.send),
            True)
        self.database.setAutoJoinPriority.assert_called_once_with(
            'botgotsthis', 0)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'priority', '0'))

    async def test_not_existing(self):
        self.database.setAutoJoinPriority.return_value = False
        self.assertIs(
            await autojoin.auto_join_priority('botgotsthis', 0, self.send),
            True)
        self.database.setAutoJoinPriority.assert_called_once_with(
            'botgotsthis', 0)
        self.send.assert_called_once_with(StrContains('botgotsthis', 'never'))


class TestManageBotAutoJoinReloadServer(asynctest.TestCase):
    def setUp(self):
        self.database = MagicMock(spec=DatabaseMain)
        self.database.__aenter__.return_value = self.database
        self.database.__aexit__.return_value = False
        self.send = Mock(spec=send)

        patcher = patch('sys.stdout', new_callable=StringIO)
        self.addCleanup(patcher.stop)
        self.mock_stdout = patcher.start()

        patcher = patch('lib.api.twitch.chat_server')
        self.addCleanup(patcher.stop)
        self.mock_server = patcher.start()

        patcher = patch.object(DatabaseMain, 'acquire')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database

        patcher = patch('bot.utils.ensureServer', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_ensure = patcher.start()

        patcher = patch('bot.utils.now', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_now = patcher.start()

    async def test_same_server(self):
        now = datetime(2000, 1, 1)
        self.mock_now.return_value = now
        self.database.getAutoJoinsChats.return_value = AsyncIterator([
            AutoJoinChannel('botgotsthis', 0, ''),
            ])
        self.mock_server.return_value = ''
        self.assertIs(await autojoin.reload_server(self.send), True)
        self.database.getAutoJoinsChats.assert_called_once_with()
        self.assertFalse(self.database.setAutoJoinServer.called)
        self.assertFalse(self.mock_ensure.called)
        self.send.assert_called_once_with(StrContains('reload', 'complete'))
        self.assertEqual(self.mock_stdout.getvalue(), '')

    async def test_server_error(self):
        now = datetime(2000, 1, 1)
        self.mock_now.return_value = now
        self.database.getAutoJoinsChats.return_value = AsyncIterator([
            AutoJoinChannel('botgotsthis', 0, ''),
            ])
        self.mock_server.return_value = None
        self.assertIs(await autojoin.reload_server(self.send), True)
        self.database.getAutoJoinsChats.assert_called_once_with()
        self.assertFalse(self.database.setAutoJoinServer.called)
        self.assertFalse(self.mock_ensure.called)
        self.send.assert_called_once_with(StrContains('reload', 'complete'))
        self.assertEqual(self.mock_stdout.getvalue(), '')

    async def test_server_different(self):
        now = datetime(2000, 1, 1)
        self.mock_now.return_value = now
        self.database.getAutoJoinsChats.return_value = AsyncIterator([
            AutoJoinChannel('botgotsthis', 0, ''),
            ])
        self.mock_server.return_value = 'twitch'
        self.assertIs(await autojoin.reload_server(self.send), True)
        self.database.getAutoJoinsChats.assert_called_once_with()
        self.database.setAutoJoinServer.assert_called_once_with('botgotsthis',
                                                                'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.send.assert_called_once_with(StrContains('reload', 'complete'))
        self.assertNotEqual(self.mock_stdout.getvalue(), '')
