import asynctest

from datetime import datetime

from asynctest.mock import MagicMock, Mock, patch

from bot.data import Channel
from lib.cache import CacheStore
from lib.data import WhisperCommandArgs
from lib.data.message import Message
from lib.data.permissions import WhisperPermissionSet
from lib.database import DatabaseMain


class TestWhisper(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.sessionData = {}
        self.data = Mock(spec=CacheStore)
        self.database = MagicMock(spec=DatabaseMain)
        self.database.__aenter__.return_value = self.database
        self.database.__aexit__.return_value = False
        self.permissionSet = {
            'owner': False,
            'manager': False,
            'staff': False,
            'admin': False,
            'globalMod': False,
            }
        self.permissions = MagicMock(spec=WhisperPermissionSet)
        self.permissions.__getitem__.side_effect = \
            lambda k: self.permissionSet[k]
        self.args = WhisperCommandArgs(
            self.data, 'botgotsthis', Message(''),
            self.permissions, self.now)

        patcher = patch.object(DatabaseMain, 'acquire')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database
