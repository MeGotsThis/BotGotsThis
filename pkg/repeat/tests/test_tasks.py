import asynctest

from datetime import datetime

from asynctest.mock import MagicMock, Mock, call, patch

from bot.data import Channel
from lib.cache import CacheStore
from lib.database import AutoRepeatMessage
from tests.unittest.mock_class import AsyncIterator
from .. import tasks


class TestRepeatTasks(asynctest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.isMod = False
        self.data = MagicMock(spec=CacheStore)
        self.data.__aenter__.return_value = self.data

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.channels = {
            'botgotsthis': self.channel,
            }

        patcher = patch('lib.cache.get_cache')
        self.addCleanup(patcher.stop)
        self.mock_data = patcher.start()
        self.mock_data.return_value = self.data

        patcher = patch('lib.helper.timeout.record_timeout')
        self.addCleanup(patcher.stop)
        self.mock_timeout = patcher.start()

        self.now = datetime(2000, 1, 1)

    async def test_empty(self):
        self.data.getAutoRepeatToSend.return_value = AsyncIterator([])
        await tasks.autoRepeatMessage(self.now)
        self.assertFalse(self.data.sentAutoRepeat.called)
        self.assertFalse(self.mock_timeout.called)
        self.assertFalse(self.channel.send.called)

    async def test_no_channel(self):
        self.data.getAutoRepeatToSend.return_value = AsyncIterator([
            AutoRepeatMessage('megotsthis', '', 'Kappa')
            ])
        await tasks.autoRepeatMessage(self.now)
        self.assertFalse(self.data.sentAutoRepeat.called)
        self.assertFalse(self.mock_timeout.called)
        self.assertFalse(self.channel.send.called)

    async def test(self):
        self.data.getAutoRepeatToSend.return_value = AsyncIterator([
            AutoRepeatMessage('botgotsthis', '', 'Kappa'),
            ])
        await tasks.autoRepeatMessage(self.now)
        self.data.sentAutoRepeat.assert_called_once_with('botgotsthis', '')
        self.assertFalse(self.mock_timeout.called)
        self.channel.send.assert_called_once_with('Kappa')

    async def test_multiple(self):
        self.data.getAutoRepeatToSend.return_value = AsyncIterator([
            AutoRepeatMessage('botgotsthis', '', 'Kappa'),
            AutoRepeatMessage('botgotsthis', 'Kappa', 'Keepo'),
            ])
        await tasks.autoRepeatMessage(self.now)
        self.data.sentAutoRepeat.assert_has_calls(
            [call('botgotsthis', ''), call('botgotsthis', 'Kappa')])
        self.assertFalse(self.mock_timeout.called)
        self.channel.send.assert_has_calls(
            [call('Kappa'), call('Keepo')])

    async def test_mod(self):
        self.channel.isMod = True
        self.data.getAutoRepeatToSend.return_value = AsyncIterator([
            AutoRepeatMessage('botgotsthis', '', 'Kappa'),
            ])
        await tasks.autoRepeatMessage(self.now)
        self.data.sentAutoRepeat.assert_called_once_with('botgotsthis', '')
        self.mock_timeout.assert_called_once_with(
            self.channel, None, 'Kappa', None, 'autorepeat')
        self.channel.send.assert_called_once_with('Kappa')
