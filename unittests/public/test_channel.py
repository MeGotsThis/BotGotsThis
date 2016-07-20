import unittest
from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from collections import defaultdict
from datetime import datetime
from source.data import ChatCommandArgs
from source.data.message import Message
from source.data.permissions import ChatPermissionSet
from source.database import DatabaseBase
from unittest.mock import MagicMock, Mock


class TestChannel(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.tags = IrcMessageTags()
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.database = Mock(spec=DatabaseBase)
        self.permissionSet = defaultdict(bool)
        self.permissions = MagicMock(spec=ChatPermissionSet)
        self.permissions.inOwnerChannel = False
        _ = lambda k: self.permissionSet[k]
        self.permissions.__getitem__.side_effect = _
        self.args = ChatCommandArgs(self.database, self.channel, self.tags,
                                    'botgotsthis', Message(''),
                                    self.permissions, self.now)
