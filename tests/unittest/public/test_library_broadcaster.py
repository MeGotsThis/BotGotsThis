import unittest
from bot import utils
from bot.data import Channel, Socket
from bot.twitchmessage import IrcMessageTags
from source.data.message import Message
from source.database import DatabaseBase
from source.public.library import broadcaster
from unittest.mock import ANY, Mock, patch


def send(messages):
    pass


class TestLibraryBroadcasterCome(unittest.TestCase):
    def setUp(self):
        self.tags = IrcMessageTags()
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.channels = {'botgotsthis': Mock(spec=Channel)}

        patcher = patch('source.api.twitch.chat_server', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_chat_server = patcher.start()

        patcher = patch('bot.utils.joinChannel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_join = patcher.start()

        patcher = patch('bot.utils.ensureServer', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_ensure = patcher.start()

    def test(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_join.return_value = True
        self.mock_globals.channels = {}
        self.assertIs(
            broadcaster.come(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.assertFalse(self.mock_ensure.called)
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')

    def test_existing(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_ensure.return_value = utils.ENSURE_CORRECT
        self.mock_join.return_value = False
        self.assertIs(
            broadcaster.come(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    def test_existing_move_server(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_ensure.return_value = utils.ENSURE_REJOIN
        self.mock_join.return_value = False
        self.assertIs(
            broadcaster.come(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    def test_existing_not_joined(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_ensure.return_value = utils.ENSURE_NOT_JOINED
        self.mock_join.return_value = False
        self.assertIs(
            broadcaster.come(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    def test_existing_unknown_cluster(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_ensure.return_value = utils.ENSURE_CLUSTER_UNKNOWN
        self.mock_join.return_value = False
        self.assertIs(
            broadcaster.come(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    def test_unknown_cluster(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_join.return_value = None
        self.assertIs(
            broadcaster.come(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.assertFalse(self.mock_ensure.called)
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_chat_server.assert_called_once_with('botgotsthis')

    def test_banned(self):
        self.database.isChannelBannedReason.return_value = ''
        self.assertIs(
            broadcaster.come(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.assertFalse(self.database.getAutoJoinsPriority.called)
        self.assertFalse(self.mock_ensure.called)
        self.assertFalse(self.mock_join.called)
        self.assertFalse(self.mock_chat_server.called)


class TestLibraryBroadcasterLeave(unittest.TestCase):
    def setUp(self):
        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.botnick = 'botgotsthis'

        self.send = Mock(spec=send)

        patcher = patch('time.sleep', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_sleep = patcher.start()

        patcher = patch('bot.utils.partChannel',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_part = patcher.start()

    def test(self):
        self.assertIs(broadcaster.leave('megotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.mock_sleep.assert_called_once_with(ANY)
        self.mock_part.assert_called_once_with('megotsthis')

    def test_bot(self):
        self.assertIs(broadcaster.leave('botgotsthis', self.send), False)
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
        self.send.assert_called_once_with(ANY)
        self.channel.clear.assert_called_once_with()

    def test_not_existing(self):
        self.assertIs(broadcaster.empty('megotsthis', self.send), True)
        self.send.assert_not_called()
        self.channel.clear.assert_not_called()


class TestLibraryBroadcasterAutoJoin(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.database.isChannelBannedReason.return_value = None
        self.send = Mock(spec=send)

        patcher = patch('source.public.library.broadcaster.auto_join_add',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_add = patcher.start()
        self.mock_add.return_value = True

        patcher = patch('source.public.library.broadcaster.auto_join_delete',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_delete = patcher.start()
        self.mock_delete.return_value = True

    def test(self):
        self.assertIs(
            broadcaster.auto_join(self.database, 'botgotsthis', self.send,
                                  Message('!autojoin')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.mock_add.assert_called_once_with(self.database, 'botgotsthis',
                                              self.send)
        self.assertFalse(self.mock_delete.called)
        self.send.assert_not_called()

    def test_add(self):
        self.assertIs(
            broadcaster.auto_join(self.database, 'botgotsthis', self.send,
                                  Message('!autojoin yes')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.mock_add.assert_called_once_with(self.database, 'botgotsthis',
                                              self.send)
        self.assertFalse(self.mock_delete.called)
        self.send.assert_not_called()

    def test_delete(self):
        self.assertIs(
            broadcaster.auto_join(self.database, 'botgotsthis', self.send,
                                  Message('!autojoin delete')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.mock_delete.assert_called_once_with(self.database, 'botgotsthis',
                                                 self.send)
        self.assertFalse(self.mock_add.called)
        self.send.assert_not_called()

    def test_banned(self):
        self.database.isChannelBannedReason.return_value = ''
        self.assertIs(
            broadcaster.auto_join(self.database, 'botgotsthis', self.send,
                                  Message('!autojoin')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_delete.called)
        self.send.assert_called_once_with(ANY)

    def test_banned_delete(self):
        self.database.isChannelBannedReason.return_value = ''
        self.assertIs(
            broadcaster.auto_join(self.database, 'botgotsthis', self.send,
                                  Message('!autojoin delete')),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_delete.called)
        self.send.assert_called_once_with(ANY)


class TestLibraryBroadcasterAutoJoinAdd(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.clusters = {'twitch': Mock(spec=Socket)}

        patcher = patch('source.api.twitch.chat_server', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_chat_server = patcher.start()

        patcher = patch('bot.utils.joinChannel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_join = patcher.start()

        patcher = patch('bot.utils.ensureServer', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_ensure = patcher.start()

    def test(self):
        self.mock_join.return_value = True
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.assertIs(
            broadcaster.auto_join_add(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(ANY)
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_not_called()
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.assertFalse(self.mock_ensure.called)

    def test_existing(self):
        self.mock_join.return_value = True
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.assertIs(
            broadcaster.auto_join_add(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(ANY)
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

    def test_joined(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_CORRECT
        self.assertIs(
            broadcaster.auto_join_add(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(ANY)
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_not_called()
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    def test_joined_existing(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_CORRECT
        self.assertIs(
            broadcaster.auto_join_add(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(ANY)
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

    def test_wrong_server(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_REJOIN
        self.assertIs(
            broadcaster.auto_join_add(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(ANY)
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_not_called()
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    def test_wrong_server_existing(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_REJOIN
        self.assertIs(
            broadcaster.auto_join_add(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(ANY)
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

    def test_not_possible_1(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_NOT_JOINED
        self.assertIs(
            broadcaster.auto_join_add(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(ANY)
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_not_called()
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    def test_not_possible_1_existing(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_NOT_JOINED
        self.assertIs(
            broadcaster.auto_join_add(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(ANY)
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

    def test_not_possible_2(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = True
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_CLUSTER_UNKNOWN
        self.assertIs(
            broadcaster.auto_join_add(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(ANY)
        self.database.discardAutoJoin.assert_not_called()
        self.database.saveAutoJoin.assert_called_once_with(
            'botgotsthis', 0, 'twitch')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.database.setAutoJoinServer.assert_not_called()
        self.mock_chat_server.assert_called_once_with('botgotsthis')
        self.mock_join.assert_called_once_with('botgotsthis', 0, 'twitch')
        self.mock_ensure.assert_called_once_with('botgotsthis', 0, 'twitch')

    def test_not_possible_2_existing(self):
        self.mock_join.return_value = False
        self.mock_chat_server.return_value = 'twitch'
        self.database.saveAutoJoin.return_value = False
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_ensure.return_value = utils.ENSURE_CLUSTER_UNKNOWN
        self.assertIs(
            broadcaster.auto_join_add(self.database, 'botgotsthis', self.send),
            True)
        self.send.assert_called_once_with(ANY)
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


class TestLibraryBroadcasterAutoJoinDelete(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

    def test(self):
        self.database.discardAutoJoin.return_value = True
        self.assertIs(
            broadcaster.auto_join_delete(self.database, 'botgotsthis',
                                         self.send),
            True)
        self.database.discardAutoJoin.assert_called_once_with('botgotsthis')
        self.send.assert_called_once_with(ANY)

    def test_not_existing(self):
        self.database.discardAutoJoin.return_value = False
        self.assertIs(
            broadcaster.auto_join_delete(self.database, 'botgotsthis',
                                         self.send),
            True)
        self.database.discardAutoJoin.assert_called_once_with('botgotsthis')
        self.send.assert_called_once_with(ANY)


class TestLibraryBroadcasterSetTimeOutLevel(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.moderatorDefaultTimeout = [60, 600, 0]

    def test_1(self):
        self.assertIs(
            broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-1 0')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength0', '0')
        self.send.assert_called_once_with(ANY)

    def test_1_default(self):
        self.assertIs(
            broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-1')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength0', None)
        self.send.assert_called_once_with(ANY)

    def test_2(self):
        self.assertIs(
            broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-2 0')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength1', '0')
        self.send.assert_called_once_with(ANY)

    def test_2_default(self):
        self.assertIs(
            broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-2')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength1', None)
        self.send.assert_called_once_with(ANY)

    def test_3(self):
        self.assertIs(
            broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-3 0')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength2', '0')
        self.send.assert_called_once_with(ANY)

    def test_3_default(self):
        self.assertIs(
            broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-3')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength2', None)
        self.send.assert_called_once_with(ANY)

    def test_0(self):
        self.assertIs(
            broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-0')),
            False)
        self.database.setChatProperty.assert_not_called()
        self.send.assert_not_called()

    def test_4(self):
        self.assertIs(
            broadcaster.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-4')),
            False)
        self.database.setChatProperty.assert_not_called()
        self.send.assert_not_called()
