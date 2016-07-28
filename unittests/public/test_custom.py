import unittest
from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from datetime import datetime
from source.data import CustomFieldArgs, CustomProcessArgs
from source.data.message import Message
from source.data.permissions import ChatPermissionSet
from source.database import DatabaseBase
from unittest.mock import MagicMock, Mock


class TestCustomField(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.args = CustomFieldArgs(
            'field', None, None, None, None, Message(''),
            'botgotsthis', 'botgotsthis', self.now)


class TestCustomProcess(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.tags = IrcMessageTags()
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.database = Mock(spec=DatabaseBase)
        self.permissionSet = {
            'owner': False,
            'inOwnerChannel': False,
            'staff': False,
            'admin': False,
            'globalMod': False,
            'broadcaster': False,
            'moderator': False,
            'subscriber': False,
            'turbo': False,
            'chatModerator': False,
            }
        self.permissions = MagicMock(spec=ChatPermissionSet)
        self.permissions.inOwnerChannel = False
        _ = lambda k: self.permissionSet[k]
        self.permissions.__getitem__.side_effect = _
        self.messages = ['Kappa']
        self.args = CustomProcessArgs(
            self.database, self.channel, self.tags, 'botgotsthis',
            self.permissions, 'botgotsthis', '', 'kappa', self.messages)