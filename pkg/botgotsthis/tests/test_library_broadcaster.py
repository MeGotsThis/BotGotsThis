import unittest

import asynctest

from asynctest.mock import Mock, patch

from bot import utils
from bot.coroutine.connection import ConnectionHandler
from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from lib.data.message import Message
from lib.database import DatabaseMain
from pkg.botgotsthis.library import broadcaster
from tests.unittest.mock_class import StrContains, TypeMatch


def send(messages):
    pass


class TestLibraryBroadcasterCome(asynctest.TestCase):
    def setUp(self):
        self.tags = IrcMessageTags()
        self.database = Mock(spec=DatabaseMain)
        self.send = Mock(spec=send)

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.channels = {'botgotsthis': Mock(spec=Channel)}

        patcher = patch('lib.api.twitch.chat_server')
        self.addCleanup(patcher.stop)
        self.mock_chat_server = patcher.start()

        patcher = patch('bot.utils.joinChannel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_join = patcher.start()

        patcher = patch('bot.utils.ensureServer', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_ensure = patcher.start()

    async def test(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_join.return_value = True
        self.mock_globals.channels = {}
        self.assertIs(
            await broadcaster.come(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('Joining', 'botgotsthis'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.assertFalse(self.mock_ensure.called)
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')

    async def test_existing(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_ensure.return_value = utils.ENSURE_CORRECT
        self.mock_join.return_value = False
        self.assertIs(
            await broadcaster.come(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(StrContains('in', 'botgotsthis'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    async def test_existing_move_server(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_ensure.return_value = utils.ENSURE_REJOIN
        self.mock_join.return_value = False
        self.assertIs(
            await broadcaster.come(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('Move', 'botgotsthis', 'server'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    async def test_existing_not_joined(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_ensure.return_value = utils.ENSURE_NOT_JOINED
        self.mock_join.return_value = False
        self.assertIs(
            await broadcaster.come(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(StrContains('Error'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    async def test_existing_unknown_cluster(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_ensure.return_value = utils.ENSURE_CLUSTER_UNKNOWN
        self.mock_join.return_value = False
        self.assertIs(
            await broadcaster.come(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(StrContains('Error'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    async def test_unknown_cluster(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_join.return_value = None
        self.assertIs(
            await broadcaster.come(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'join', 'server'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.assertFalse(self.mock_ensure.called)
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')

    async def test_banned(self):
        self.database.isChannelBannedReason.return_value = ''
        self.assertIs(
            await broadcaster.come(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'banned'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.assertFalse(self.database.getAutoJoinsPriority.called)
        self.assertFalse(self.mock_ensure.called)
        self.assertFalse(self.mock_join.called)
        self.assertFalse(self.mock_chat_server.called)


class TestLibraryBroadcasterLeave(asynctest.TestCase):
    def setUp(self):
        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.botnick = 'botgotsthis'

        self.send = Mock(spec=send)

        patcher = patch('asyncio.sleep')
        self.addCleanup(patcher.stop)
        self.mock_sleep = patcher.start()

        patcher = patch('bot.utils.partChannel',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_part = patcher.start()

    async def test(self):
        self.assertIs(await broadcaster.leave('megotsthis', self.send), True)
        self.send.assert_called_once_with(StrContains('megotsthis', 'Bye'))
        self.mock_sleep.assert_called_once_with(TypeMatch(float))
        self.mock_part.assert_called_once_with('megotsthis')

    async def test_bot(self):
        self.assertIs(await broadcaster.leave('botgotsthis', self.send), False)
        self.send.assert_not_called()
        self.assertFalse(self.mock_sleep.called)
        self.assertFalse(self.mock_part.called)


class TestLibraryBroadcasterEmpty(unittest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.send = Mock(spec=send)

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.channels = {'botgotsthis': self.channel}

    def test(self):
        self.assertIs(broadcaster.empty('botgotsthis', self.send), True)
        self.send.assert_called_once_with(
            StrContains('Clear', 'messages', 'botgotsthis'))
        self.channel.clear.assert_called_once_with()

    def test_not_existing(self):
        self.assertIs(broadcaster.empty('megotsthis', self.send), True)
        self.send.assert_not_called()
        self.channel.clear.assert_not_called()


class TestLibraryBroadcasterAutoJoin(asynctest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseMain)
        self.database.isChannelBannedReason.return_value = None
        self.send = Mock(spec=send)

        patcher = patch('pkg.botgotsthis.library.broadcaster.auto_join_add')
        self.addCleanup(patcher.stop)
        self.mock_add = patcher.start()
        self.mock_add.return_value = True

        patcher = patch('pkg.botgotsthis.library.broadcaster.auto_join_delete')
        self.addCleanup(patcher.stop)
        self.mock_delete = patcher.start()
        self.mock_delete.return_value = True

    async def test(self):
        self.assertIs(
            await broadcaster.auto_join(self.database, 'botgotsthis',
                                        self.send, Message('!autojoin')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.mock_add.assert_called_once_with(self.database, 'botgotsthis',
                                              self.send)
        self.assertFalse(self.mock_delete.called)
        self.send.assert_not_called()

    async def test_add(self):
        self.assertIs(
            await broadcaster.auto_join(self.database, 'botgotsthis',
                                        self.send, Message('!autojoin yes')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.mock_add.assert_called_once_with(self.database, 'botgotsthis',
                                              self.send)
        self.assertFalse(self.mock_delete.called)
        self.send.assert_not_called()

    async def test_delete(self):
        self.assertIs(
            await broadcaster.auto_join(
                self.database, 'botgotsthis', self.send,
                Message('!autojoin delete')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.mock_delete.assert_called_once_with(self.database, 'botgotsthis',
                                                 self.send)
        self.assertFalse(self.mock_add.called)
        self.send.assert_not_called()

    async def test_banned(self):
        self.database.isChannelBannedReason.return_value = ''
        self.assertIs(
            await broadcaster.auto_join(self.database, 'botgotsthis',
                                        self.send, Message('!autojoin')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_delete.called)
        self.send.assert_called_once_with(StrContains('banned', 'botgotsthis'))

    async def test_banned_delete(self):
        self.database.isChannelBannedReason.return_value = ''
        self.assertIs(
            await broadcaster.auto_join(
                self.database, 'botgotsthis', self.send,
                Message('!autojoin delete')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_delete.called)
        self.send.assert_called_once_with(StrContains('banned', 'botgotsthis'))


class TestLibraryBroadcasterAutoJoinAdd(asynctest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseMain)
        self.send = Mock(spec=send)

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.clusters = {'twitch': Mock(spec=ConnectionHandler)}

        patcher = patch('lib.api.twitch.chat_server')
        self.addCleanup(patcher.stop)
        self.mock_chat_server = patcher.start()

        patcher = patch('bot.utils.joinChannel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_join = patcher.start()

        patcher = patch('bot.utils.ensureServer', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_ensure = patcher.start()

    async def test(self):
        self.mock_join.return_value = True
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.assertIs(
            await broadcaster.auto_join_add(self.database, 'botgotsthis',
                                            self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'enable', 'join'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_not_called()
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.assertFalse(self.mock_ensure.called)

    async def test_existing(self):
        self.mock_join.return_value = True
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.assertIs(
            await broadcaster.auto_join_add(self.database, 'botgotsthis',
                                            self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'already'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_called_once_with(
            'botgotsthis', 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.assertFalse(self.mock_ensure.called)

    async def test_joined(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_CORRECT
        self.assertIs(
            await broadcaster.auto_join_add(self.database, 'botgotsthis',
                                            self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'enabled'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_not_called()
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    async def test_joined_existing(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_CORRECT
        self.assertIs(
            await broadcaster.auto_join_add(self.database, 'botgotsthis',
                                            self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'already', 'enable', 'in chat'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_called_once_with(
            'botgotsthis', 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    async def test_wrong_server(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_REJOIN
        self.assertIs(
            await broadcaster.auto_join_add(self.database, 'botgotsthis',
                                            self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'enable'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_not_called()
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    async def test_wrong_server_existing(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_REJOIN
        self.assertIs(
            await broadcaster.auto_join_add(self.database, 'botgotsthis',
                                            self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'already', 'enable', 'move', 'server'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_called_once_with(
            'botgotsthis', 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    async def test_not_possible_1(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_NOT_JOINED
        self.assertIs(
            await broadcaster.auto_join_add(self.database, 'botgotsthis',
                                            self.send),
            True)
        self.send.assert_called_once_with(StrContains('botgotsthis', 'enable'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_not_called()
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    async def test_not_possible_1_existing(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_NOT_JOINED
        self.assertIs(
            await broadcaster.auto_join_add(self.database, 'botgotsthis',
                                            self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'already', 'enabled', 'in chat'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_called_once_with(
            'botgotsthis', 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    async def test_not_possible_2(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_CLUSTER_UNKNOWN
        self.assertIs(
            await broadcaster.auto_join_add(self.database, 'botgotsthis',
                                            self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'enabled', 'move', 'server'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_not_called()
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    async def test_not_possible_2_existing(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_CLUSTER_UNKNOWN
        self.assertIs(
            await broadcaster.auto_join_add(self.database, 'botgotsthis',
                                            self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'enabled', 'move', 'server'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_called_once_with(
            'botgotsthis', 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')


class TestLibraryBroadcasterAutoJoinDelete(asynctest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseMain)
        self.send = Mock(spec=send)

    async def test(self):
        self.database.discardAutoJoin.return_value = True
        self.assertIs(
            await broadcaster.auto_join_delete(self.database, 'botgotsthis',
                                               self.send),
            True)
        self.database.discardAutoJoin.assert_called_once_with('botgotsthis')
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'disable'))

    async def test_not_existing(self):
        self.database.discardAutoJoin.return_value = False
        self.assertIs(
            await broadcaster.auto_join_delete(self.database, 'botgotsthis',
                                               self.send),
            True)
        self.database.discardAutoJoin.assert_called_once_with('botgotsthis')
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'never'))


class TestLibraryBroadcasterSetTimeOutLevel(asynctest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseMain)
        self.send = Mock(spec=send)

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.moderatorDefaultTimeout = [60, 600, 0]

    async def test_1(self):
        self.assertIs(
            await broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-1 1')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength0', '1')
        self.send.assert_called_once_with(
            StrContains('timeout', '1st', '1 second'))

    async def test_1_default(self):
        self.assertIs(
            await broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-1')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength0', None)
        self.send.assert_called_once_with(
            StrContains('timeout', '1st', 'default'))

    async def test_2(self):
        self.assertIs(
            await broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-2 3600')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength1', '3600')
        self.send.assert_called_once_with(
            StrContains('timeout', '2nd', '3600 seconds'))

    async def test_2_default(self):
        self.assertIs(
            await broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-2')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength1', None)
        self.send.assert_called_once_with(
            StrContains('timeout', '2nd', 'default'))

    async def test_3(self):
        self.assertIs(
            await broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-3 0')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength2', '0')
        self.send.assert_called_once_with(
            StrContains('timeout', '3rd', 'ban'))

    async def test_3_default(self):
        self.assertIs(
            await broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-3')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength2', None)
        self.send.assert_called_once_with(
            StrContains('timeout', '3rd', 'default'))

    async def test_0(self):
        self.assertIs(
            await broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-0')),
            False)
        self.database.setChatProperty.assert_not_called()
        self.send.assert_not_called()

    async def test_4(self):
        self.assertIs(
            await broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-4')),
            False)
        self.database.setChatProperty.assert_not_called()
        self.send.assert_not_called()
