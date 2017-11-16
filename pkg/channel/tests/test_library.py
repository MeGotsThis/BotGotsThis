import asynctest

from asynctest.mock import MagicMock, Mock, patch

from bot.coroutine.connection import ConnectionHandler
from bot.twitchmessage import IrcMessageTags
from lib.data.message import Message
from lib.database import DatabaseMain
from tests.unittest.mock_class import StrContains, TypeMatch

from .. import library


def send(messages):
    pass


class TestLibraryBroadcasterCome(asynctest.TestCase):
    def setUp(self):
        self.tags = IrcMessageTags()
        self.database = MagicMock(spec=DatabaseMain)
        self.database.__aenter__.return_value = self.database
        self.database.__aexit__.return_value = False
        self.send = Mock(spec=send)

        patcher = patch('bot.utils.joinChannel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_join = patcher.start()

        patcher = patch.object(DatabaseMain, 'acquire')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database

    async def test(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_join.return_value = True
        self.assertIs(
            await library.come('botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('Joining', 'botgotsthis'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0)

    async def test_existing(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_join.return_value = False
        self.assertIs(
            await library.come('botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(StrContains('in', 'botgotsthis'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0)

    async def test_banned(self):
        self.database.isChannelBannedReason.return_value = ''
        self.assertIs(
            await library.come('botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'banned'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.assertFalse(self.database.getAutoJoinsPriority.called)
        self.assertFalse(self.mock_join.called)


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
        self.assertIs(await library.leave('megotsthis', self.send), True)
        self.send.assert_called_once_with(StrContains('megotsthis', 'Bye'))
        self.mock_sleep.assert_called_once_with(TypeMatch(float))
        self.mock_part.assert_called_once_with('megotsthis')

    async def test_bot(self):
        self.assertIs(await library.leave('botgotsthis', self.send), False)
        self.send.assert_not_called()
        self.assertFalse(self.mock_sleep.called)
        self.assertFalse(self.mock_part.called)


class TestLibraryBroadcasterAutoJoin(asynctest.TestCase):
    def setUp(self):
        self.database = MagicMock(spec=DatabaseMain)
        self.database.__aenter__.return_value = self.database
        self.database.__aexit__.return_value = False
        self.database.isChannelBannedReason.return_value = None
        self.send = Mock(spec=send)

        patcher = patch.object(DatabaseMain, 'acquire')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database

        patcher = patch(library.__name__ + '.auto_join_add')
        self.addCleanup(patcher.stop)
        self.mock_add = patcher.start()
        self.mock_add.return_value = True

        patcher = patch(library.__name__ + '.auto_join_delete')
        self.addCleanup(patcher.stop)
        self.mock_delete = patcher.start()
        self.mock_delete.return_value = True

    async def test(self):
        self.assertIs(
            await library.auto_join('botgotsthis', self.send,
                                    Message('!autojoin')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.mock_add.assert_called_once_with(self.database, 'botgotsthis',
                                              self.send)
        self.assertFalse(self.mock_delete.called)
        self.send.assert_not_called()

    async def test_add(self):
        self.assertIs(
            await library.auto_join('botgotsthis', self.send,
                                    Message('!autojoin yes')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.mock_add.assert_called_once_with(self.database, 'botgotsthis',
                                              self.send)
        self.assertFalse(self.mock_delete.called)
        self.send.assert_not_called()

    async def test_delete(self):
        self.assertIs(
            await library.auto_join('botgotsthis', self.send,
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
            await library.auto_join('botgotsthis', self.send,
                                    Message('!autojoin')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_delete.called)
        self.send.assert_called_once_with(StrContains('banned', 'botgotsthis'))

    async def test_banned_delete(self):
        self.database.isChannelBannedReason.return_value = ''
        self.assertIs(
            await library.auto_join('botgotsthis', self.send,
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
        self.mock_globals.cluster = Mock(spec=ConnectionHandler)

        patcher = patch('bot.utils.joinChannel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_join = patcher.start()

    async def test(self):
        self.mock_join.return_value = True
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.assertIs(
            await library.auto_join_add(self.database, 'botgotsthis',
                                        self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'enable', 'join'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with('botgotsthis', 0)
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0)

    async def test_existing(self):
        self.mock_join.return_value = True
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.assertIs(
            await library.auto_join_add(self.database, 'botgotsthis',
                                        self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'already'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with('botgotsthis', 0)
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0)

    async def test_joined(self):
        self.mock_join.return_value = False
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.assertIs(
            await library.auto_join_add(self.database, 'botgotsthis',
                                        self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'enabled'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with('botgotsthis', 0)
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0)

    async def test_joined_existing(self):
        self.mock_join.return_value = False
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.assertIs(
            await library.auto_join_add(self.database, 'botgotsthis',
                                        self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'already', 'enable', 'in chat'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with('botgotsthis', 0)
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0)

    async def test_not_possible_1(self):
        self.mock_join.return_value = False
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.assertIs(
            await library.auto_join_add(self.database, 'botgotsthis',
                                        self.send),
            True)
        self.send.assert_called_once_with(StrContains('botgotsthis', 'enable'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with('botgotsthis', 0)
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0)

    async def test_not_possible_1_existing(self):
        self.mock_join.return_value = False
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.assertIs(
            await library.auto_join_add(self.database, 'botgotsthis',
                                        self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'already', 'enabled', 'in chat'))
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with('botgotsthis', 0)
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0)


class TestLibraryBroadcasterAutoJoinDelete(asynctest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseMain)
        self.send = Mock(spec=send)

    async def test(self):
        self.database.discardAutoJoin.return_value = True
        self.assertIs(
            await library.auto_join_delete(self.database, 'botgotsthis',
                                           self.send),
            True)
        self.database.discardAutoJoin.assert_called_once_with('botgotsthis')
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'disable'))

    async def test_not_existing(self):
        self.database.discardAutoJoin.return_value = False
        self.assertIs(
            await library.auto_join_delete(self.database, 'botgotsthis',
                                           self.send),
            True)
        self.database.discardAutoJoin.assert_called_once_with('botgotsthis')
        self.send.assert_called_once_with(
            StrContains('botgotsthis', 'never'))
