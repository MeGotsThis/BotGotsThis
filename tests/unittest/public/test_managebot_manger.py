import asynctest

from asynctest.mock import Mock, patch

from source.data import Message
from source.database import DatabaseMain
from tests.unittest.base_managebot import TestManageBot, send
from tests.unittest.mock_class import StrContains

# Needs to be imported last
from source.public.manage import manager


class TestManageBotManager(TestManageBot):
    def setUp(self):
        super().setUp()
        self.permissionSet['owner'] = True
        self.database.isChannelBannedReason.return_value = None

    async def test_false(self):
        self.assertIs(await manager.manageManager(self.args), False)
        self.permissionSet['owner'] = False
        args = self.args._replace(message=Message('!managebot'))
        self.assertIs(await manager.manageManager(args), False)
        args = self.args._replace(message=Message('!managebot manager'))
        self.assertIs(await manager.manageManager(args), False)
        message = Message('!managebot manager no_action')
        args = self.args._replace(message=message)
        self.assertIs(await manager.manageManager(args), False)
        message = Message('!managebot manager no_action some_user')
        args = self.args._replace(message=message)
        self.assertIs(await manager.manageManager(args), False)
        self.permissionSet['owner'] = True
        args = self.args._replace(message=Message('!managebot manager'))
        self.assertIs(await manager.manageManager(args), False)
        args = self.args._replace(message=Message('!managebot manager'))
        self.assertIs(await manager.manageManager(args), False)
        message = Message('!managebot manager no_action')
        args = self.args._replace(message=message)
        self.assertIs(await manager.manageManager(args), False)
        message = Message('!managebot manager no_action some_user')
        args = self.args._replace(message=message)
        self.assertIs(await manager.manageManager(args), False)
        self.assertFalse(self.send.called)

    @patch('source.public.manage.manager.insert_manager')
    async def test_add(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot manager add botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await manager.manageManager(args), True)
        mock_add.assert_called_once_with(
            'botgotsthis', self.database, self.send)

    @patch('source.public.manage.manager.insert_manager')
    async def test_insert(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot manager insert botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await manager.manageManager(args), True)
        mock_add.assert_called_once_with(
            'botgotsthis', self.database, self.send)

    @patch('source.public.manage.manager.delete_manager')
    async def test_delete(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot manager delete botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await manager.manageManager(args), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', self.database, self.send)

    @patch('source.public.manage.manager.delete_manager')
    async def test_del(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot manager del botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await manager.manageManager(args), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', self.database, self.send)

    @patch('source.public.manage.manager.delete_manager')
    async def test_remove(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot manager remove botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await manager.manageManager(args), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', self.database, self.send)

    @patch('source.public.manage.manager.delete_manager')
    async def test_rem(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot manager rem botgotsthis')
        args = self.args._replace(message=message)
        self.assertIs(await manager.manageManager(args), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', self.database, self.send)


class TestManageBotManagerInsertManager(asynctest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseMain)
        self.send = Mock(spec=send)

    async def test(self):
        self.database.isBotManager.return_value = False
        self.database.addBotManager.return_value = True
        self.assertIs(
            await manager.insert_manager('megotsthis', self.database,
                                         self.send),
            True)
        self.database.isBotManager.assert_called_once_with('megotsthis')
        self.database.addBotManager.assert_called_once_with('megotsthis')
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'manager'))

    async def test_manager(self):
        self.database.isBotManager.return_value = True
        self.assertIs(
            await manager.insert_manager('megotsthis', self.database,
                                         self.send),
            True)
        self.database.isBotManager.assert_called_once_with('megotsthis')
        self.assertFalse(self.database.addBotManager.called)
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'already', 'manager'))

    async def test_database_error(self):
        self.database.isBotManager.return_value = False
        self.database.addBotManager.return_value = False
        self.assertIs(
            await manager.insert_manager('megotsthis', self.database,
                                         self.send),
            True)
        self.database.isBotManager.assert_called_once_with('megotsthis')
        self.database.addBotManager.assert_called_once_with('megotsthis')
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'not', 'add', 'manager', 'Error'))


class TestManageBotManagerDeleteManager(asynctest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseMain)
        self.send = Mock(spec=send)

    async def test(self):
        self.database.isBotManager.return_value = True
        self.database.removeBotManager.return_value = True
        self.assertIs(
            await manager.delete_manager('megotsthis', self.database,
                                         self.send),
            True)
        self.database.isBotManager.assert_called_once_with('megotsthis')
        self.database.removeBotManager.assert_called_once_with('megotsthis')
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'remove', 'manager'))

    async def test_not_manager(self):
        self.database.isBotManager.return_value = False
        self.assertIs(
            await manager.delete_manager('megotsthis', self.database,
                                         self.send),
            True)
        self.database.isBotManager.assert_called_once_with('megotsthis')
        self.assertFalse(self.database.removeBotManager.called)
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'not', 'manager'))

    async def test_database_error(self):
        self.database.isBotManager.return_value = True
        self.database.removeBotManager.return_value = False
        self.assertIs(
            await manager.delete_manager('megotsthis', self.database,
                                         self.send),
            True)
        self.database.isBotManager.assert_called_once_with('megotsthis')
        self.database.removeBotManager.assert_called_once_with('megotsthis')
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'not', 'manager', 'Error'))
