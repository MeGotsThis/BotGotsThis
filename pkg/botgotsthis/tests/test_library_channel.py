import math
import unittest

import asynctest

from asynctest.mock import MagicMock, Mock, patch

from bot.data import Channel
from lib.database import DatabaseMain
from tests.unittest.mock_class import StrContains
from ..library import channel


def send(messages):
    pass


class TestLibraryChannelJoin(asynctest.TestCase):
    def setUp(self):
        self.database = MagicMock(spec=DatabaseMain)
        self.database.__aenter__.return_value = self.database
        self.database.__aexit__.return_value = False
        self.send = Mock(spec=send)

        patcher = patch.object(DatabaseMain, 'acquire')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database

        patcher = patch('bot.utils.joinChannel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_join = patcher.start()

    async def test(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = math.inf
        self.mock_join.return_value = True
        self.assertIs(
            await channel.join('botgotsthis', self.send), True)
        self.send.assert_called_once_with(StrContains('Join', 'botgotsthis'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_with('botgotsthis', math.inf)

    async def test_auto_join(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = 0
        self.mock_join.return_value = True
        self.assertIs(
            await channel.join('botgotsthis', self.send), True)
        self.send.assert_called_once_with(StrContains('Join', 'botgotsthis'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_with('botgotsthis', 0)

    async def test_already_joined(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.getAutoJoinsPriority.return_value = math.inf
        self.mock_join.return_value = False
        self.assertIs(
            await channel.join('botgotsthis', self.send), True)
        self.send.assert_called_once_with(
            StrContains('Already', 'join', 'botgotsthis'))
        self.database.isChannelBannedReason.assert_called_once_with(
            'botgotsthis')
        self.database.getAutoJoinsPriority.assert_called_once_with(
            'botgotsthis')
        self.mock_join.assert_called_with('botgotsthis', math.inf)


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
        self.assertIs(channel.part('megotsthis', self.send), True)
        self.send.assert_called_with(StrContains('Leav', 'megotsthis'))
        self.mock_part.assert_called_with('megotsthis')

    def test_bot_channel(self):
        self.assertIs(channel.part('botgotsthis', self.send), False)
        self.send.assert_not_called()
        self.assertFalse(self.mock_part.called)


class TestLibraryChannelSay(asynctest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.channels = {'botgotsthis': self.channel}

        patcher = patch('lib.helper.timeout.record_timeout')
        self.addCleanup(patcher.stop)
        self.mock_record = patcher.start()

    async def test(self):
        self.assertIs(
            await channel.say('megotsthis', 'botgotsthis', 'Kappa'),
            True)
        self.mock_record.assert_called_once_with(
            self.channel, 'megotsthis', 'Kappa', None, 'say')
        self.channel.send.assert_called_once_with('Kappa')

    async def test_not_existing(self):
        self.assertIs(
            await channel.say('botgotsthis', 'megotsthis', 'Kappa'),
            False)
        self.assertFalse(self.mock_record.called)
        self.channel.send.assert_not_called()


class TestLibraryChannelEmptyAll(unittest.TestCase):
    @patch('bot.utils.clearAllChat', autospec=True)
    def test(self, mock_clear):
        mock_send = Mock(spec=send)
        self.assertIs(channel.empty_all(mock_send), True)
        mock_clear.assert_called_once_with()
        mock_send.assert_called_once_with(StrContains('all', 'messages'))


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
        self.send.assert_called_once_with(
            StrContains('all', 'messages', 'botgotsthis'))
        self.channel.clear.assert_called_once_with()

    def test_non_existing(self):
        self.assertIs(channel.empty('', self.send), False)
        self.assertFalse(self.send.called)
        self.channel.clear.assert_not_called()
