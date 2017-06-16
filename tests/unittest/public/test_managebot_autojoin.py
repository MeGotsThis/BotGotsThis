import unittest

import asynctest

from datetime import datetime
from io import StringIO

from asynctest.mock import Mock, patch

from source.data import Message
from source.database import AutoJoinChannel, DatabaseBase
from source.public.manage import autojoin
from tests.unittest.base_managebot import TestManageBot, send
from tests.unittest.mock_class import StrContains


class TestManageBotAutoJoin(TestManageBot):
    def setUp(self):
        super().setUp()
        self.database.isChannelBannedReason.return_value = None

    def test_false(self):
        self.assertIs(autojoin.manageAutoJoin(self.args), False)
        message = Message('!managebot')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)),
            False)
        message = Message('!managebot autojoin')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)),
            False)
        message = Message('!managebot autojoin no_action')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)),
            False)
        self.assertFalse(self.database.isChannelBannedReason.called)
        message = Message('!managebot autojoin no_action no_arg')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)),
            False)
        self.assertFalse(self.send.called)
        self.database.isChannelBannedReason.assert_called_with('no_arg')

    @patch('source.public.manage.autojoin.reload_server', autospec=True)
    def test_banned_channel(self, mock_reload):
        self.database.isChannelBannedReason.return_value = 'Reason'
        mock_reload.return_value = True
        message = Message('!managebot autojoin action banned_channel')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        self.send.assert_called_once_with(StrContains('banned_channel', 'ban'))

    @patch('source.public.manage.autojoin.reload_server', autospec=True)
    def test_banned_channel_blank(self, mock_reload):
        self.database.isChannelBannedReason.return_value = ''
        mock_reload.return_value = True
        message = Message('!managebot autojoin action banned_channel')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        self.send.assert_called_once_with(StrContains('banned_channel', 'ban'))

    @patch('source.public.manage.autojoin.reload_server', autospec=True)
    def test_reloadserver(self, mock_reload):
        mock_reload.return_value = True
        message = Message('!managebot autojoin reloadserver')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_reload.assert_called_once_with(self.database, self.send)

    @patch('source.public.library.broadcaster.auto_join_add', autospec=True)
    def test_add(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot autojoin add botgotsthis')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_add.assert_called_once_with(self.database, 'botgotsthis',
                                         self.send)

    @patch('source.public.library.broadcaster.auto_join_add', autospec=True)
    def test_insert(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot autojoin insert botgotsthis')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_add.assert_called_once_with(self.database, 'botgotsthis',
                                         self.send)

    @patch('source.public.library.broadcaster.auto_join_add', autospec=True)
    def test_join(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot autojoin join botgotsthis')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_add.assert_called_once_with(self.database, 'botgotsthis',
                                         self.send)

    @patch('source.public.library.broadcaster.auto_join_delete', autospec=True)
    def test_delete(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin delete botgotsthis')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(self.database, 'botgotsthis',
                                            self.send)

    @patch('source.public.library.broadcaster.auto_join_delete', autospec=True)
    def test_del(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin del botgotsthis')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(self.database, 'botgotsthis',
                                            self.send)

    @patch('source.public.library.broadcaster.auto_join_delete', autospec=True)
    def test_remove(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin remove botgotsthis')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(self.database, 'botgotsthis',
                                            self.send)

    @patch('source.public.library.broadcaster.auto_join_delete', autospec=True)
    def test_rem(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin rem botgotsthis')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(self.database, 'botgotsthis',
                                            self.send)

    @patch('source.public.library.broadcaster.auto_join_delete', autospec=True)
    def test_part(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin part botgotsthis')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(self.database, 'botgotsthis',
                                            self.send)

    @patch('source.public.manage.autojoin.auto_join_priority', autospec=True)
    def test_priority(self, mock_priority):
        mock_priority.return_value = True
        message = Message('!managebot autojoin priority botgotsthis')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_priority.assert_called_once_with(self.database, 'botgotsthis', 0,
                                              self.send)

    @patch('source.public.manage.autojoin.auto_join_priority', autospec=True)
    def test_pri(self, mock_priority):
        mock_priority.return_value = True
        message = Message('!managebot autojoin pri botgotsthis')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_priority.assert_called_once_with(self.database, 'botgotsthis', 0,
                                              self.send)

    @patch('source.public.manage.autojoin.auto_join_priority', autospec=True)
    def test_priority_gibberish(self, mock_priority):
        mock_priority.return_value = True
        message = Message('!managebot autojoin priority botgotsthis abc')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_priority.assert_called_once_with(self.database, 'botgotsthis', 0,
                                              self.send)

    @patch('source.public.manage.autojoin.auto_join_priority', autospec=True)
    def test_priority_integer(self, mock_priority):
        mock_priority.return_value = True
        message = Message('!managebot autojoin priority botgotsthis 1')
        self.assertIs(
            autojoin.manageAutoJoin(self.args._replace(message=message)), True)
        mock_priority.assert_called_once_with(self.database, 'botgotsthis', 1,
                                              self.send)


class TestManageBotAutoJoinAutoJoinPriority(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

    def test(self):
        self.database.setAutoJoinPriority.return_value = True
        self.assertIs(
            autojoin.auto_join_priority(self.database, 'botgotsthis', 0,
                                        self.send),
            True)
        self.database.setAutoJoinPriority.assert_called_once_with(
            'botgotsthis', 0)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'priority', '0'))

    def test_not_existing(self):
        self.database.setAutoJoinPriority.return_value = False
        self.assertIs(
            autojoin.auto_join_priority(self.database, 'botgotsthis', 0,
                                        self.send),
            True)
        self.database.setAutoJoinPriority.assert_called_once_with(
            'botgotsthis', 0)
        self.send.assert_called_once_with(StrContains('botgotsthis', 'never'))


class TestManageBotAutoJoinReloadServer(asynctest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

        patcher = patch('sys.stdout', new_callable=StringIO)
        self.addCleanup(patcher.stop)
        self.mock_stdout = patcher.start()

        patcher = patch('source.api.twitch.chat_server')
        self.addCleanup(patcher.stop)
        self.mock_server = patcher.start()

        patcher = patch('bot.utils.ensureServer', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_ensure = patcher.start()

        patcher = patch('bot.utils.now', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_now = patcher.start()

    def test_same_server(self):
        now = datetime(2000, 1, 1)
        self.mock_now.return_value = now
        self.database.getAutoJoinsChats.return_value = [
            AutoJoinChannel('botgotsthis', 0, ''),
            ]
        self.mock_server.return_value = ''
        message = Message('!managebot reload')
        self.assertIs(autojoin.reload_server(self.database, self.send), True)
        self.database.getAutoJoinsChats.assert_called_once_with()
        self.assertFalse(self.database.setAutoJoinServer.called)
        self.assertFalse(self.mock_ensure.called)
        self.send.assert_called_once_with(StrContains('reload', 'complete'))
        self.assertEqual(self.mock_stdout.getvalue(), '')

    def test_server_error(self):
        now = datetime(2000, 1, 1)
        self.mock_now.return_value = now
        self.database.getAutoJoinsChats.return_value = [
            AutoJoinChannel('botgotsthis', 0, ''),
            ]
        self.mock_server.return_value = None
        message = Message('!managebot reload')
        self.assertIs(autojoin.reload_server(self.database, self.send), True)
        self.database.getAutoJoinsChats.assert_called_once_with()
        self.assertFalse(self.database.setAutoJoinServer.called)
        self.assertFalse(self.mock_ensure.called)
        self.send.assert_called_once_with(StrContains('reload', 'complete'))
        self.assertEqual(self.mock_stdout.getvalue(), '')

    def test_server_different(self):
        now = datetime(2000, 1, 1)
        self.mock_now.return_value = now
        self.database.getAutoJoinsChats.return_value = [
            AutoJoinChannel('botgotsthis', 0, ''),
            ]
        self.mock_server.return_value = 'twitch'
        message = Message('!managebot reload')
        self.assertIs(autojoin.reload_server(self.database, self.send), True)
        self.database.getAutoJoinsChats.assert_called_once_with()
        self.database.setAutoJoinServer.assert_called_once_with('botgotsthis',
                                                                'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.send.assert_called_once_with(StrContains('reload', 'complete'))
        self.assertNotEqual(self.mock_stdout.getvalue(), '')
