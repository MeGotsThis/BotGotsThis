import math
import unittest
from bot import utils
from bot.data import Channel, Socket
from source.database import DatabaseBase
from source.public.library import channel
from unittest.mock import ANY, Mock, patch


def send(messages):
    pass


class TestLibraryChannelJoin(unittest.TestCase):
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
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = math.inf
        self.mock_chat_server.return_value = 'twitch'
        self.mock_join.return_value = True
        self.assertIs(
            channel.join(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_chat_server.assert_called_with('botgotsthis')
        self.mock_join.assert_called_with('botgotsthis', math.inf, 'twitch')
        self.assertFalse(self.mock_ensure.called)

    def test_invalid_cluster(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = math.inf
        self.mock_chat_server.return_value = ''
        self.assertIs(
            channel.join(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_chat_server.assert_called_with('botgotsthis')
        self.assertFalse(self.mock_join.called)
        self.assertFalse(self.mock_ensure.called)

    def test_auto_join(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_chat_server.return_value = 'twitch'
        self.mock_join.return_value = True
        self.assertIs(
            channel.join(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_chat_server.assert_called_with('botgotsthis')
        self.mock_join.assert_called_with('botgotsthis', 0, 'twitch')
        self.assertFalse(self.mock_ensure.called)

    def test_already_joined(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = math.inf
        self.mock_chat_server.return_value = 'twitch'
        self.mock_join.return_value = False
        self.mock_ensure.return_value = utils.ENSURE_CORRECT
        self.assertIs(
            channel.join(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_chat_server.assert_called_with('botgotsthis')
        self.mock_join.assert_called_with('botgotsthis', math.inf, 'twitch')
        self.mock_ensure.assert_called_with('botgotsthis', math.inf, 'twitch')

    def test_already_joined_changed_cluster(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = math.inf
        self.mock_chat_server.return_value = 'twitch'
        self.mock_join.return_value = False
        self.mock_ensure.return_value = utils.ENSURE_REJOIN
        self.assertIs(
            channel.join(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_chat_server.assert_called_with('botgotsthis')
        self.mock_join.assert_called_with('botgotsthis', math.inf, 'twitch')
        self.mock_ensure.assert_called_with('botgotsthis', math.inf, 'twitch')

    def test_already_joined_invalid_1(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = math.inf
        self.mock_chat_server.return_value = 'twitch'
        self.mock_join.return_value = False
        self.mock_ensure.return_value = utils.ENSURE_CLUSTER_UNKNOWN
        self.assertIs(
            channel.join(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_chat_server.assert_called_with('botgotsthis')
        self.mock_join.assert_called_with('botgotsthis', math.inf, 'twitch')
        self.mock_ensure.assert_called_with('botgotsthis', math.inf, 'twitch')

    def test_already_joined_invalid_2(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = math.inf
        self.mock_chat_server.return_value = 'twitch'
        self.mock_join.return_value = False
        self.mock_ensure.return_value = utils.ENSURE_NOT_JOINED
        self.assertIs(
            channel.join(self.database, 'botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_chat_server.assert_called_with('botgotsthis')
        self.mock_join.assert_called_with('botgotsthis', math.inf, 'twitch')
        self.mock_ensure.assert_called_with('botgotsthis', math.inf, 'twitch')


class TestLibraryChannelPart(unittest.TestCase):
    def setUp(self):
        self.send = Mock(spec=send)

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.botnick = 'botgotsthis'

        patcher = patch('bot.utils.partChannel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_part = patcher.start()

    def test(self):
        self.assertIs(channel.part('', self.send), True)
        self.send.assert_called_with(ANY)
        self.mock_part.assert_called_with('')

    def test_bot_channel(self):
        self.assertIs(channel.part('botgotsthis', self.send), False)
        self.send.assert_not_called()
        self.assertFalse(self.mock_part.called)


class TestLibraryChannelSay(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.channel = Mock(spec=Channel)

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.channels = {'botgotsthis': self.channel}

        patcher = patch('source.public.library.timeout.record_timeout',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_record = patcher.start()

    def test(self):
        self.assertIs(
            channel.say(self.database, 'megotsthis', 'botgotsthis', 'Kappa'),
            True)
        self.mock_record.assert_called_once_with(
            self.database, self.channel, 'megotsthis', 'Kappa', None, ANY)
        self.channel.send.assert_called_once_with('Kappa')

    def test_not_existing(self):
        self.assertIs(
            channel.say(self.database, 'botgotsthis', 'megotsthis', 'Kappa'),
            False)
        self.assertFalse(self.mock_record.called)
        self.channel.send.assert_not_called()


class TestLibraryChannelEmptyAll(unittest.TestCase):
    @patch('bot.utils.clearAllChat', autospec=True)
    def test(self, mock_clear):
        mock_send = Mock(spec=send)
        self.assertIs(channel.empty_all(mock_send), True)
        mock_clear.assert_called_once_with()
        mock_send.assert_called_once_with(ANY)


class TestLibraryChannelEmpty(unittest.TestCase):
    def setUp(self):
        self.send = Mock(spec=send)
        self.channel = Mock(spec=Channel)

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.channels = {'botgotsthis': self.channel}

    def test(self):
        self.assertIs(channel.empty('botgotsthis', self.send), True)
        self.send.assert_called_once_with(ANY)
        self.channel.clear.assert_called_once_with()

    def test_non_existing(self):
        self.assertIs(channel.empty('', self.send), False)
        self.assertFalse(self.send.called)
        self.channel.clear.assert_not_called()
