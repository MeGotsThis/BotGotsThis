import unittest
from bot.data import Channel
from datetime import datetime
from source.database import DatabaseBase, AutoRepeatMessage
from source.public.tasks import repeat
from unittest.mock import Mock, call, patch


class TestTasksRepeat(unittest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.isMod = False
        self.database = Mock(spec=DatabaseBase)

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.channels = {
            'botgotsthis': self.channel,
            }

        patcher = patch('source.database.factory.getDatabase', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value.__enter__.return_value = self.database

        patcher = patch('source.public.library.timeout.record_timeout',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_timeout = patcher.start()

        self.now = datetime(2000, 1, 1)

    def test_empty(self):
        self.database.getAutoRepeatToSend.return_value = []
        repeat.autoRepeatMessage(self.now)
        self.assertFalse(self.database.sentAutoRepeat.called)
        self.assertFalse(self.mock_timeout.called)
        self.assertFalse(self.channel.send.called)

    def test_no_channel(self):
        self.database.getAutoRepeatToSend.return_value = [
            AutoRepeatMessage('megotsthis', '', 'Kappa')
            ]
        repeat.autoRepeatMessage(self.now)
        self.assertFalse(self.database.sentAutoRepeat.called)
        self.assertFalse(self.mock_timeout.called)
        self.assertFalse(self.channel.send.called)

    def test(self):
        self.database.getAutoRepeatToSend.return_value = [
            AutoRepeatMessage('botgotsthis', '', 'Kappa'),
            ]
        repeat.autoRepeatMessage(self.now)
        self.database.sentAutoRepeat.assert_called_once_with('botgotsthis', '')
        self.assertFalse(self.mock_timeout.called)
        self.channel.send.assert_called_once_with('Kappa')

    def test_multiple(self):
        self.database.getAutoRepeatToSend.return_value = [
            AutoRepeatMessage('botgotsthis', '', 'Kappa'),
            AutoRepeatMessage('botgotsthis', 'Kappa', 'Keepo'),
            ]
        repeat.autoRepeatMessage(self.now)
        self.database.sentAutoRepeat.assert_has_calls(
            [call('botgotsthis', ''), call('botgotsthis', 'Kappa')])
        self.assertFalse(self.mock_timeout.called)
        self.channel.send.assert_has_calls(
            [call('Kappa'), call('Keepo')])

    def test_mod(self):
        self.channel.isMod = True
        self.database.getAutoRepeatToSend.return_value = [
            AutoRepeatMessage('botgotsthis', '', 'Kappa'),
            ]
        repeat.autoRepeatMessage(self.now)
        self.database.sentAutoRepeat.assert_called_once_with('botgotsthis', '')
        self.mock_timeout.assert_called_once_with(
            self.database, self.channel, None, 'Kappa', None, 'autorepeat')
        self.channel.send.assert_called_once_with('Kappa')
