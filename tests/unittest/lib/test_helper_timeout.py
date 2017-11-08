from datetime import datetime, timedelta

import asynctest
from asynctest.mock import MagicMock, Mock, call, patch

from bot.data import Channel
from lib.cache import CacheStore
from lib.database import DatabaseTimeout
from lib.helper import timeout
from tests.unittest.mock_class import TypeMatch


class TestLibraryTimeoutUser(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.dbtimeout = MagicMock(spec=DatabaseTimeout)
        self.dbtimeout.__aenter__.return_value = self.dbtimeout
        self.data = MagicMock(spec=CacheStore)
        self.data.getChatProperties.return_value = {
            'timeoutLength0': 60,
            'timeoutLength1': 3600,
            'timeoutLength2': 86400,
            }
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.sessionData = {}

        patcher = patch.object(DatabaseTimeout, 'acquire')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.dbtimeout

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.moderatorDefaultTimeout = [60, 3600, 86400]
        self.mock_config.warningDuration = 7200

        patcher = patch('bot.utils.whisper', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_whisper = patcher.start()

        patcher = patch('bot.utils.now', autospec=True, return_value=self.now)
        self.addCleanup(patcher.stop)
        self.mock_now = patcher.start()

    async def test(self):
        await timeout.timeout_user(self.data, self.channel, 'megotsthis',
                                   'unittest')
        self.data.getChatProperties.assert_called_once_with(
            'botgotsthis',
            ['timeoutLength0', 'timeoutLength1', 'timeoutLength2'],
            TypeMatch(dict), int)
        self.assertIn('timeouts', self.channel.sessionData)
        self.assertIn('unittest', self.channel.sessionData['timeouts'])
        self.assertIn('megotsthis',
                      self.channel.sessionData['timeouts']['unittest'])
        self.assertEqual(
            self.channel.sessionData['timeouts']['unittest']['megotsthis'],
            (self.now, 0))
        self.channel.send.assert_called_once_with('.timeout megotsthis 60 ', 0)
        self.mock_database.assert_called_once_with()
        self.dbtimeout.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 0, 60, None, None)
        self.assertFalse(self.mock_whisper.called)

    async def test_reason(self):
        await timeout.timeout_user(self.data, self.channel, 'megotsthis',
                                   'unittest', reason='Kappa')
        self.data.getChatProperties.assert_called_once_with(
            'botgotsthis',
            ['timeoutLength0', 'timeoutLength1', 'timeoutLength2'],
            TypeMatch(dict), int)
        self.assertIn('timeouts', self.channel.sessionData)
        self.assertIn('unittest', self.channel.sessionData['timeouts'])
        self.assertIn('megotsthis',
                      self.channel.sessionData['timeouts']['unittest'])
        self.assertEqual(
            self.channel.sessionData['timeouts']['unittest']['megotsthis'],
            (self.now, 0))
        self.channel.send.assert_called_once_with(
            '.timeout megotsthis 60 Kappa', 0)
        self.mock_database.assert_called_once_with()
        self.dbtimeout.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 0, 60, None,
            'Kappa')

    async def test_message(self):
        await timeout.timeout_user(self.data, self.channel, 'megotsthis',
                                   'unittest', message='Kappa')
        self.data.getChatProperties.assert_called_once_with(
            'botgotsthis',
            ['timeoutLength0', 'timeoutLength1', 'timeoutLength2'],
            TypeMatch(dict), int)
        self.assertIn('timeouts', self.channel.sessionData)
        self.assertIn('unittest', self.channel.sessionData['timeouts'])
        self.assertIn('megotsthis',
                      self.channel.sessionData['timeouts']['unittest'])
        self.assertEqual(
            self.channel.sessionData['timeouts']['unittest']['megotsthis'],
            (self.now, 0))
        self.channel.send.assert_called_once_with('.timeout megotsthis 60 ', 0)
        self.mock_database.assert_called_once_with()
        self.dbtimeout.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 0, 60, 'Kappa',
            None)
        self.assertFalse(self.mock_whisper.called)

    async def test_base_level_1(self):
        await timeout.timeout_user(self.data, self.channel, 'megotsthis',
                                   'unittest', base_level=1)
        self.data.getChatProperties.assert_called_once_with(
            'botgotsthis',
            ['timeoutLength0', 'timeoutLength1', 'timeoutLength2'],
            TypeMatch(dict), int)
        self.assertIn('timeouts', self.channel.sessionData)
        self.assertIn('unittest', self.channel.sessionData['timeouts'])
        self.assertIn('megotsthis',
                      self.channel.sessionData['timeouts']['unittest'])
        self.assertEqual(
            self.channel.sessionData['timeouts']['unittest']['megotsthis'],
            (self.now, 1))
        self.channel.send.assert_called_once_with(
            '.timeout megotsthis 3600 ', 0)
        self.mock_database.assert_called_once_with()
        self.dbtimeout.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 1, 3600, None, None)
        self.assertFalse(self.mock_whisper.called)

    async def test_base_level_2(self):
        await timeout.timeout_user(self.data, self.channel, 'megotsthis',
                                   'unittest', base_level=2)
        self.data.getChatProperties.assert_called_once_with(
            'botgotsthis',
            ['timeoutLength0', 'timeoutLength1', 'timeoutLength2'],
            TypeMatch(dict), int)
        self.assertIn('timeouts', self.channel.sessionData)
        self.assertIn('unittest', self.channel.sessionData['timeouts'])
        self.assertIn('megotsthis',
                      self.channel.sessionData['timeouts']['unittest'])
        self.assertEqual(
            self.channel.sessionData['timeouts']['unittest']['megotsthis'],
            (self.now, 2))
        self.channel.send.assert_called_once_with(
            '.timeout megotsthis 86400 ', 0)
        self.mock_database.assert_called_once_with()
        self.dbtimeout.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 2, 86400, None,
            None)
        self.assertFalse(self.mock_whisper.called)

    async def test_base_level_3(self):
        await timeout.timeout_user(self.data, self.channel, 'megotsthis',
                                   'unittest', base_level=3)
        self.data.getChatProperties.assert_called_once_with(
            'botgotsthis',
            ['timeoutLength0', 'timeoutLength1', 'timeoutLength2'],
            TypeMatch(dict), int)
        self.assertIn('timeouts', self.channel.sessionData)
        self.assertIn('unittest', self.channel.sessionData['timeouts'])
        self.assertIn('megotsthis',
                      self.channel.sessionData['timeouts']['unittest'])
        self.assertEqual(
            self.channel.sessionData['timeouts']['unittest']['megotsthis'],
            (self.now, 2))
        self.channel.send.assert_called_once_with(
            '.timeout megotsthis 86400 ', 0)
        self.mock_database.assert_called_once_with()
        self.dbtimeout.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 2, 86400, None,
            None)
        self.assertFalse(self.mock_whisper.called)

    async def test_base_level_negative(self):
        await timeout.timeout_user(self.data, self.channel, 'megotsthis',
                                   'unittest', base_level=-1)
        self.data.getChatProperties.assert_called_once_with(
            'botgotsthis',
            ['timeoutLength0', 'timeoutLength1', 'timeoutLength2'],
            TypeMatch(dict), int)
        self.assertIn('timeouts', self.channel.sessionData)
        self.assertIn('unittest', self.channel.sessionData['timeouts'])
        self.assertIn('megotsthis',
                      self.channel.sessionData['timeouts']['unittest'])
        self.assertEqual(
            self.channel.sessionData['timeouts']['unittest']['megotsthis'],
            (self.now, 0))
        self.channel.send.assert_called_once_with('.timeout megotsthis 60 ', 0)
        self.mock_database.assert_called_once_with()
        self.dbtimeout.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 0, 60, None, None)
        self.assertFalse(self.mock_whisper.called)

    async def test_override(self):
        self.data.getChatProperties.return_value = {
            'timeoutLength0': 1,
            'timeoutLength1': 1,
            'timeoutLength2': 1,
            }
        await timeout.timeout_user(self.data, self.channel, 'megotsthis',
                                   'unittest')
        self.data.getChatProperties.assert_called_once_with(
            'botgotsthis',
            ['timeoutLength0', 'timeoutLength1', 'timeoutLength2'],
            TypeMatch(dict), int)
        self.assertIn('timeouts', self.channel.sessionData)
        self.assertIn('unittest', self.channel.sessionData['timeouts'])
        self.assertIn('megotsthis',
                      self.channel.sessionData['timeouts']['unittest'])
        self.assertEqual(
            self.channel.sessionData['timeouts']['unittest']['megotsthis'],
            (self.now, 0))
        self.channel.send.assert_called_once_with('.timeout megotsthis 1 ', 0)
        self.mock_database.assert_called_once_with()
        self.dbtimeout.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 0, 1, None, None)
        self.assertFalse(self.mock_whisper.called)

    async def test_ban(self):
        self.data.getChatProperties.return_value = {
            'timeoutLength0': 0,
            'timeoutLength1': 0,
            'timeoutLength2': 0,
            }
        await timeout.timeout_user(self.data, self.channel, 'megotsthis',
                                   'unittest')
        self.data.getChatProperties.assert_called_once_with(
            'botgotsthis',
            ['timeoutLength0', 'timeoutLength1', 'timeoutLength2'],
            TypeMatch(dict), int)
        self.assertIn('timeouts', self.channel.sessionData)
        self.assertIn('unittest', self.channel.sessionData['timeouts'])
        self.assertIn('megotsthis',
                      self.channel.sessionData['timeouts']['unittest'])
        self.assertEqual(
            self.channel.sessionData['timeouts']['unittest']['megotsthis'],
            (self.now, 0))
        self.channel.send.assert_called_once_with('.ban megotsthis ', 0)
        self.mock_database.assert_called_once_with()
        self.dbtimeout.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 0, 0, None, None)
        self.assertFalse(self.mock_whisper.called)

    async def test_repeat_0(self):
        self.channel.sessionData['timeouts'] = {
            'unittest': {
                'megotsthis': (self.now - timedelta(seconds=1), 0)
                }
            }
        await timeout.timeout_user(self.data, self.channel, 'megotsthis',
                                   'unittest')
        self.data.getChatProperties.assert_called_once_with(
            'botgotsthis',
            ['timeoutLength0', 'timeoutLength1', 'timeoutLength2'],
            TypeMatch(dict), int)
        self.assertIn('timeouts', self.channel.sessionData)
        self.assertIn('unittest', self.channel.sessionData['timeouts'])
        self.assertIn('megotsthis',
                      self.channel.sessionData['timeouts']['unittest'])
        self.assertEqual(
            self.channel.sessionData['timeouts']['unittest']['megotsthis'],
            (self.now, 1))
        self.channel.send.assert_called_once_with(
            '.timeout megotsthis 3600 ', 0)
        self.mock_database.assert_called_once_with()
        self.dbtimeout.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 1, 3600, None, None)
        self.assertFalse(self.mock_whisper.called)

    async def test_repeat_1(self):
        self.channel.sessionData['timeouts'] = {
            'unittest': {
                'megotsthis': (self.now - timedelta(seconds=1), 1)
                }
            }
        await timeout.timeout_user(self.data, self.channel, 'megotsthis',
                                   'unittest')
        self.data.getChatProperties.assert_called_once_with(
            'botgotsthis',
            ['timeoutLength0', 'timeoutLength1', 'timeoutLength2'],
            TypeMatch(dict), int)
        self.assertIn('timeouts', self.channel.sessionData)
        self.assertIn('unittest', self.channel.sessionData['timeouts'])
        self.assertIn('megotsthis',
                      self.channel.sessionData['timeouts']['unittest'])
        self.assertEqual(
            self.channel.sessionData['timeouts']['unittest']['megotsthis'],
            (self.now, 2))
        self.channel.send.assert_called_once_with(
            '.timeout megotsthis 86400 ', 0)
        self.mock_database.assert_called_once_with()
        self.dbtimeout.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 2, 86400, None,
            None)
        self.assertFalse(self.mock_whisper.called)

    async def test_repeat_2(self):
        self.channel.sessionData['timeouts'] = {
            'unittest': {
                'megotsthis': (self.now - timedelta(seconds=1), 2)
                }
            }
        await timeout.timeout_user(self.data, self.channel, 'megotsthis',
                                   'unittest')
        self.data.getChatProperties.assert_called_once_with(
            'botgotsthis',
            ['timeoutLength0', 'timeoutLength1', 'timeoutLength2'],
            TypeMatch(dict), int)
        self.assertIn('timeouts', self.channel.sessionData)
        self.assertIn('unittest', self.channel.sessionData['timeouts'])
        self.assertIn('megotsthis',
                      self.channel.sessionData['timeouts']['unittest'])
        self.assertEqual(
            self.channel.sessionData['timeouts']['unittest']['megotsthis'],
            (self.now, 2))
        self.channel.send.assert_called_once_with(
            '.timeout megotsthis 86400 ', 0)
        self.mock_database.assert_called_once_with()
        self.dbtimeout.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 2, 86400, None,
            None)
        self.assertFalse(self.mock_whisper.called)


class TestLibraryTimeoutRecord(asynctest.TestCase):
    def setUp(self):
        self.database = MagicMock(spec=DatabaseTimeout)
        self.database.__aenter__.return_value = self.database
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'

        patcher = patch.object(DatabaseTimeout, 'acquire')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database

    async def test(self):
        await timeout.record_timeout(
            self.channel, None, 'Kappa', 'Kappa', 'unittest')
        self.assertFalse(self.database.recordTimeout.called)

    async def test_timeout(self):
        await timeout.record_timeout(
            self.channel, None, '.timeout megotsthis', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, None, 'Kappa',
            None)

    async def test_timeout_length(self):
        await timeout.record_timeout(
            self.channel, None, '.timeout megotsthis 1', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, 1, 'Kappa',
            None)

    async def test_timeout_length_reason(self):
        await timeout.record_timeout(
            self.channel, None,
            '.timeout megotsthis 1 :P', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, 1, 'Kappa',
            ':P')

    async def test_slash_timeout(self):
        await timeout.record_timeout(
            self.channel, None, '/timeout megotsthis', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, None, 'Kappa',
            None)

    async def test_slash_timeout_length(self):
        await timeout.record_timeout(
            self.channel, None, '/timeout megotsthis 1', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, 1, 'Kappa',
            None)

    async def test_slash_timeout_length_reason(self):
        await timeout.record_timeout(
            self.channel, None,
            '/timeout megotsthis 1 :P', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, 1, 'Kappa',
            ':P')

    async def test_ban(self):
        await timeout.record_timeout(
            self.channel, None, '.ban megotsthis', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, 0, 'Kappa',
            None)

    async def test_ban_reason(self):
        await timeout.record_timeout(
            self.channel, None, '.ban megotsthis :P', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, 0, 'Kappa',
            ':P')

    async def test_slash_ban(self):
        await timeout.record_timeout(
            self.channel, None, '/ban megotsthis', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, 0, 'Kappa',
            None)

    async def test_slash_ban_reason(self):
        await timeout.record_timeout(
            self.channel, None, '/ban megotsthis :P', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, 0, 'Kappa',
            ':P')

    async def test_bad(self):
        await timeout.record_timeout(
            self.channel, None, '.ban', 'Kappa', 'unittest')
        await timeout.record_timeout(
            self.channel, None, '.timeout', 'Kappa', 'unittest')
        await timeout.record_timeout(
            self.channel, None, '.timeout megotsthis abc', 'Kappa', 'unittest')
        self.assertFalse(self.database.recordTimeout.called)

    async def test_who(self):
        await timeout.record_timeout(
            self.channel, 'mebotsthis',
            '.timeout megotsthis', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', 'mebotsthis', 'unittest', None, None,
            'Kappa', None)

    async def test_multiple(self):
        await timeout.record_timeout(
            self.channel, None,
            ['.timeout megotsthis 1', '.ban megotsthis'],
            'Kappa', 'unittest')
        self.assertEqual(
            self.database.recordTimeout.mock_calls,
            [call('botgotsthis', 'megotsthis', None, 'unittest', None, 1,
                  'Kappa', None),
             call('botgotsthis', 'megotsthis', None, 'unittest', None, 0,
                  'Kappa', None),
             ])
