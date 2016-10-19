import unittest
from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from datetime import datetime
from source.data import WhisperCommandArgs
from source.data.message import Message
from source.data.permissions import WhisperPermissionSet
from source.database import DatabaseBase
from unittest.mock import MagicMock, Mock


class TestWhisper(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.sessionData = {}
        self.database = Mock(spec=DatabaseBase)
        self.permissionSet = {
            'owner': False,
            'manager': False,
            'staff': False,
            'admin': False,
            'globalMod': False,
            }
        self.permissions = MagicMock(spec=WhisperPermissionSet)
        _ = lambda k: self.permissionSet[k]
        self.permissions.__getitem__.side_effect = _
        self.args = WhisperCommandArgs(self.database, 'botgotsthis',
                                       Message(''), self.permissions, self.now)
