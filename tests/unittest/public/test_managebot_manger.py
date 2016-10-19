import unittest
from unittest.mock import Mock, patch

from source.data import Message
from source.database import DatabaseBase
from source.public.manage import manager
from tests.unittest.base_managebot import TestManageBot, send
from tests.unittest.mock_class import StrContains


class TestManageBotManager(TestManageBot):
    def setUp(self):
        super().setUp()
        self.permissionSet['owner'] = True
        self.database.isChannelBannedReason.return_value = None

    def test_false(self):
        self.assertIs(manager.manageManager(self.args), False)
        self.permissionSet['owner'] = False
        message = Message('!managebot')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)),
            False)
        message = Message('!managebot manager')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)),
            False)
        message = Message('!managebot manager no_action')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)),
            False)
        message = Message('!managebot manager no_action some_user')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)),
            False)
        self.permissionSet['owner'] = True
        message = Message('!managebot')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)),
            False)
        message = Message('!managebot manager')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)),
            False)
        message = Message('!managebot manager no_action')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)),
            False)
        message = Message('!managebot manager no_action some_user')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)),
            False)
        self.assertFalse(self.send.called)

    @patch('source.public.manage.manager.insert_manager')
    def test_add(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot manager add botgotsthis')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)), True)
        mock_add.assert_called_once_with(
            'botgotsthis', self.database, self.send)

    @patch('source.public.manage.manager.insert_manager')
    def test_insert(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot manager insert botgotsthis')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)), True)
        mock_add.assert_called_once_with(
            'botgotsthis', self.database, self.send)

    @patch('source.public.manage.manager.delete_manager')
    def test_delete(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot manager delete botgotsthis')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', self.database, self.send)

    @patch('source.public.manage.manager.delete_manager')
    def test_del(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot manager del botgotsthis')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', self.database, self.send)

    @patch('source.public.manage.manager.delete_manager')
    def test_remove(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot manager remove botgotsthis')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', self.database, self.send)

    @patch('source.public.manage.manager.delete_manager')
    def test_rem(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot manager rem botgotsthis')
        self.assertIs(
            manager.manageManager(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', self.database, self.send)


class TestManageBotManagerInsertManager(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

    def test(self):
        self.database.isBotManager.return_value = False
        self.database.addBotManager.return_value = True
        self.assertIs(
            manager.insert_manager('megotsthis', self.database, self.send),
            True)
        self.database.isBotManager.assert_called_once_with('megotsthis')
        self.database.addBotManager.assert_called_once_with('megotsthis')
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'manager'))

    def test_manager(self):
        self.database.isBotManager.return_value = True
        self.assertIs(
            manager.insert_manager('megotsthis', self.database, self.send),
            True)
        self.database.isBotManager.assert_called_once_with('megotsthis')
        self.assertFalse(self.database.addBotManager.called)
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'already', 'manager'))

    def test_database_error(self):
        self.database.isBotManager.return_value = False
        self.database.addBotManager.return_value = False
        self.assertIs(
            manager.insert_manager('megotsthis', self.database, self.send),
            True)
        self.database.isBotManager.assert_called_once_with('megotsthis')
        self.database.addBotManager.assert_called_once_with('megotsthis')
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'not', 'add', 'manager', 'Error'))


class TestManageBotManagerDeleteManager(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

    def test(self):
        self.database.isBotManager.return_value = True
        self.database.removeBotManager.return_value = True
        self.assertIs(
            manager.delete_manager('megotsthis', self.database, self.send),
            True)
        self.database.isBotManager.assert_called_once_with('megotsthis')
        self.database.removeBotManager.assert_called_once_with('megotsthis')
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'remove', 'manager'))

    def test_not_manager(self):
        self.database.isBotManager.return_value = False
        self.assertIs(
            manager.delete_manager('megotsthis', self.database, self.send),
            True)
        self.database.isBotManager.assert_called_once_with('megotsthis')
        self.assertFalse(self.database.removeBotManager.called)
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'not', 'manager'))

    def test_database_error(self):
        self.database.isBotManager.return_value = True
        self.database.removeBotManager.return_value = False
        self.assertIs(
            manager.delete_manager('megotsthis', self.database, self.send),
            True)
        self.database.isBotManager.assert_called_once_with('megotsthis')
        self.database.removeBotManager.assert_called_once_with('megotsthis')
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'not', 'manager', 'Error'))
