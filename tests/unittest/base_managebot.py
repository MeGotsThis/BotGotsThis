from datetime import datetime

import asynctest
from asynctest.mock import MagicMock, Mock

from lib.data import ManageBotArgs
from lib.data.message import Message
from lib.data.permissions import ChatPermissionSet
from lib.database import DatabaseMain


def send(messages):
    pass


class TestManageBot(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.send = Mock(spec=send)
        self.database = Mock(spec=DatabaseMain)
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
        self.permissions.__getitem__.side_effect = \
            lambda k: self.permissionSet[k]
        self.args = ManageBotArgs(self.database, self.permissions, self.send,
                                  'botgotsthis', Message(''))
