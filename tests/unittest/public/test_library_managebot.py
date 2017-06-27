import asynctest

from asynctest.mock import CoroutineMock, Mock, patch

from source.data import ManageBotArgs
from source.data.message import Message
from source.data.permissions import ChatPermissionSet
from source.database import DatabaseMain
from source.public.library import managebot
from tests.unittest.mock_class import TypeMatch


def send(messages):
    pass


def method(args):
    return True


class TestLibraryManageBot(asynctest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseMain)
        self.permissions = Mock(spec=ChatPermissionSet)
        self.send = Mock(spec=send)
        self.method = CoroutineMock(spec=method, return_value=True)

        patcher = patch('lists.manage')
        self.addCleanup(patcher.stop)
        self.mock_manage = patcher.start()
        self.mock_manage.methods.return_value = {
            'method': self.method,
            'none': None,
            }

    async def test(self):
        message = Message('!managebot method')
        self.assertIs(
            await managebot.manage_bot(self.database, self.permissions,
                                       self.send, 'managebot', message),
            True)
        self.assertFalse(self.send.called)
        self.method.assert_called_once_with(TypeMatch(ManageBotArgs))

    async def test_not_existing(self):
        message = Message('!managebot not_existing')
        self.assertIs(
            await managebot.manage_bot(self.database, self.permissions,
                                       self.send, 'managebot', message),
            False)
        self.assertFalse(self.send.called)
        self.assertFalse(self.method.called)

    async def test_none(self):
        message = Message('!managebot none')
        self.assertIs(
            await managebot.manage_bot(self.database, self.permissions,
                                       self.send, 'managebot', message),
            False)
        self.assertFalse(self.send.called)
        self.assertFalse(self.method.called)
