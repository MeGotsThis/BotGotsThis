import unittest

import asynctest

from asynctest.mock import Mock, patch

from bot.data import Channel
from lib.data.message import Message
from lib.database import DatabaseMain
from pkg.botgotsthis.library import chat
from tests.unittest.mock_class import StrContains


def send(messages):
    pass


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
        self.assertIs(chat.empty('botgotsthis', self.send), True)
        self.send.assert_called_once_with(
            StrContains('Clear', 'messages', 'botgotsthis'))
        self.channel.clear.assert_called_once_with()

    def test_not_existing(self):
        self.assertIs(chat.empty('megotsthis', self.send), True)
        self.send.assert_not_called()
        self.channel.clear.assert_not_called()


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
            await chat.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-1 1')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength0', '1')
        self.send.assert_called_once_with(
            StrContains('timeout', '1st', '1 second'))

    async def test_1_default(self):
        self.assertIs(
            await chat.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-1')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength0', None)
        self.send.assert_called_once_with(
            StrContains('timeout', '1st', 'default'))

    async def test_2(self):
        self.assertIs(
            await chat.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-2 3600')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength1', '3600')
        self.send.assert_called_once_with(
            StrContains('timeout', '2nd', '3600 seconds'))

    async def test_2_default(self):
        self.assertIs(
            await chat.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-2')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength1', None)
        self.send.assert_called_once_with(
            StrContains('timeout', '2nd', 'default'))

    async def test_3(self):
        self.assertIs(
            await chat.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-3 0')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength2', '0')
        self.send.assert_called_once_with(
            StrContains('timeout', '3rd', 'ban'))

    async def test_3_default(self):
        self.assertIs(
            await chat.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-3')),
            True)
        self.database.setChatProperty.assert_called_once_with(
            'botgotsthis', 'timeoutLength2', None)
        self.send.assert_called_once_with(
            StrContains('timeout', '3rd', 'default'))

    async def test_0(self):
        self.assertIs(
            await chat.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-0')),
            False)
        self.database.setChatProperty.assert_not_called()
        self.send.assert_not_called()

    async def test_4(self):
        self.assertIs(
            await chat.set_timeout_level(
                self.database, 'botgotsthis', self.send,
                Message('!settimeoutlevel-4')),
            False)
        self.database.setChatProperty.assert_not_called()
        self.send.assert_not_called()
