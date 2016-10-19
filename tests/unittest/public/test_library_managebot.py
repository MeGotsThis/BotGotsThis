import unittest
from source.data import ManageBotArgs
from source.data.message import Message
from source.data.permissions import ChatPermissionSet
from source.database import DatabaseBase
from source.public.library import managebot
from tests.unittest.mock_class import TypeMatch
from unittest.mock import Mock, patch


def send(messages):
    pass


def method(args):
    return True


class TestLibraryManageBot(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.permissions = Mock(spec=ChatPermissionSet)
        self.send = Mock(spec=send)
        self.method = Mock(spec=method, return_value=True)

        patcher = patch.dict('lists.manage.methods')
        self.addCleanup(patcher.stop)
        patcher.start()
        managebot.lists.manage.methods['method'] = self.method
        managebot.lists.manage.methods['none'] = None

    def test(self):
        message = Message('!managebot method')
        self.assertIs(
            managebot.manage_bot(self.database, self.permissions, self.send,
                                 'managebot', message),
            True)
        self.assertFalse(self.send.called)
        self.method.assert_called_once_with(TypeMatch(ManageBotArgs))

    def test_not_existing(self):
        message = Message('!managebot not_existing')
        self.assertIs(
            managebot.manage_bot(self.database, self.permissions, self.send,
                                 'managebot', message),
            False)
        self.assertFalse(self.send.called)
        self.assertFalse(self.method.called)

    def test_none(self):
        message = Message('!managebot none')
        self.assertIs(
            managebot.manage_bot(self.database, self.permissions, self.send,
                                 'managebot', message),
            False)
        self.assertFalse(self.send.called)
        self.assertFalse(self.method.called)
