import asynctest

import lists.manage

from datetime import datetime

from asynctest.mock import MagicMock, Mock

from source.data import ManageBotArgs
from source.data.message import Message
from source.data.permissions import ChatPermissionSet
from source.database import DatabaseBase


def send(messages):
    pass


class TestManageBot(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.send = Mock(spec=send)
        self.database = Mock(spec=DatabaseBase)
        self.permissionSet = {
            'owner': False,
            'manager': False,
            'inOwnerChannel': False,
            'staff': False,
            'admin': False,
            'globalMod': False,
            'broadcaster': False,
            'moderator': False,
            'subscriber': False,
            'permitted': False,
            'chatModerator': False,
            'bannable': True,
            }
        self.permissions = MagicMock(spec=ChatPermissionSet)
        _ = lambda k: self.permissionSet[k]
        self.permissions.__getitem__.side_effect = _
        self.args = ManageBotArgs(self.database, self.permissions, self.send,
                                  'botgotsthis', Message(''))
