import asynctest

import bot  # noqa: F401

from asynctest.mock import MagicMock, Mock, patch

from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from datetime import datetime
from lib.cache import CacheStore
from lib.data import CustomFieldArgs, CustomProcessArgs
from lib.data.message import Message
from lib.data.permissions import ChatPermissionSet
from lib.database import DatabaseMain


class TestCustomField(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.permissions = MagicMock(spec=ChatPermissionSet)
        self.args = CustomFieldArgs(
            'field', None, None, None, None, Message(''),
            'botgotsthis', 'botgotsthis', self.permissions, self.now)


class TestCustomProcess(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.tags = IrcMessageTags()
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.data = Mock(spec=CacheStore)
        self.database = MagicMock(spec=DatabaseMain)
        self.database.__aenter__.return_value = self.database
        self.database.__aexit__.return_value = False
        self.permissionSet = {
            'owner': False,
            'inOwnerChannel': False,
            'staff': False,
            'admin': False,
            'globalMod': False,
            'broadcaster': False,
            'moderator': False,
            'subscriber': False,
            'chatModerator': False,
            }
        self.permissions = MagicMock(spec=ChatPermissionSet)
        self.permissions.inOwnerChannel = False
        self.permissions.__getitem__.side_effect = \
            lambda k: self.permissionSet[k]
        self.messages = ['Kappa']
        self.args = CustomProcessArgs(
            self.data, self.channel, self.tags, 'botgotsthis',
            self.permissions, 'botgotsthis', '', 'kappa', self.messages)

        patcher = patch('lib.database.get_main_database')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database
