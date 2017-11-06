import asynctest

from asynctest.mock import CoroutineMock, Mock, patch

from lib.cache import CacheStore
from lib.data import ManageBotArgs
from lib.data.message import Message
from lib.data.permissions import ChatPermissionSet
from lib.database import DatabaseMain
from tests.unittest.mock_class import TypeMatch
from ..library import managebot


def send(messages):
    pass


def method(args):
    return True


class TestLibraryManageBot(asynctest.TestCase):
    def setUp(self):
        self.data = Mock(spec=CacheStore)
        self.database = Mock(spec=DatabaseMain)
        self.permissions = Mock(spec=ChatPermissionSet)
        self.send = Mock(spec=send)
        self.method = CoroutineMock(spec=method, return_value=True)

        patcher = patch('lib.items.manage')
        self.addCleanup(patcher.stop)
        self.mock_manage = patcher.start()
        self.mock_manage.methods.return_value = {
            'method': self.method,
            'none': None,
            }

    async def test(self):
        message = Message('!managebot method')
        self.assertIs(
            await managebot.manage_bot(
                self.data, self.permissions, self.send, 'managebot', message),
            True)
        self.assertFalse(self.send.called)
        self.method.assert_called_once_with(TypeMatch(ManageBotArgs))

    async def test_not_existing(self):
        message = Message('!managebot not_existing')
        self.assertIs(
            await managebot.manage_bot(
                self.data, self.permissions, self.send, 'managebot', message),
            False)
        self.assertFalse(self.send.called)
        self.assertFalse(self.method.called)

    async def test_none(self):
        message = Message('!managebot none')
        self.assertIs(
            await managebot.manage_bot(
                self.data, self.permissions, self.send, 'managebot', message),
            False)
        self.assertFalse(self.send.called)
        self.assertFalse(self.method.called)
