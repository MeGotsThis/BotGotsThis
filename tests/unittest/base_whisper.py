import asynctest

from datetime import datetime

from asynctest.mock import MagicMock, Mock

from bot.data import Channel
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
        self.database = Mock(spec=DatabaseMain)
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
        self.args = WhisperCommandArgs(self.database, 'botgotsthis',
                                       Message(''), self.permissions, self.now)
