import asynctest

import bot  # noqa: F401

from datetime import datetime

from asynctest.mock import MagicMock, Mock

from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from lib.data import ChatCommandArgs
from lib.data.message import Message
from lib.data.permissions import ChatPermissionSet
from lib.database import DatabaseMain


class TestChannel(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.tags = IrcMessageTags()
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.sessionData = {}
        self.database = Mock(spec=DatabaseMain)
        self.features = []
        self.database.hasFeature.side_effect = lambda c, f: f in self.features
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
        self.permissions.inOwnerChannel = False
        self.permissions.__getitem__.side_effect = \
            lambda k: self.permissionSet[k]
        self.args = ChatCommandArgs(self.database, self.channel, self.tags,
                                    'botgotsthis', Message(''),
                                    self.permissions, self.now)
