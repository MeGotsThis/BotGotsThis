from datetime import datetime

import asynctest
from asynctest.mock import MagicMock, Mock, patch

from lib.cache import CacheStore
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
        self.data = Mock(spec=CacheStore)
        self.database = MagicMock(spec=DatabaseMain)
        self.database.__aenter__.return_value = self.database
        self.database.__aexit__.return_value = False
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
        self.args = ManageBotArgs(self.data, self.permissions, self.send,
                                  'botgotsthis', Message(''))

        patcher = patch.object(DatabaseMain, 'acquire')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database
