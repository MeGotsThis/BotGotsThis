import unittest
from bot.data import Channel
from datetime import datetime, timedelta
from source.database import DatabaseBase
from source.public.library import timeout
from tests.unittest.mock_class import StrContains, TypeMatch
from unittest.mock import Mock, call, patch


class TestLibraryTimeoutUser(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.database = Mock(spec=DatabaseBase)
        self.database.getChatProperties.return_value = {
            'timeoutLength0': 60,
            'timeoutLength1': 3600,
            'timeoutLength2': 86400,
            }
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.sessionData = {}

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

    def test(self):
        timeout.timeout_user(self.database, self.channel, 'megotsthis',
                             'unittest')
        self.database.getChatProperties.assert_called_once_with(
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
        self.channel.send.assert_called_once_with('.timeout megotsthis 60', 0)
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 0, 60, None, None)
        self.assertFalse(self.mock_whisper.called)

    def test_reason(self):
        timeout.timeout_user(self.database, self.channel, 'megotsthis',
                             'unittest', reason='Kappa')
        self.database.getChatProperties.assert_called_once_with(
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
        self.channel.send.assert_called_once_with('.timeout megotsthis 60', 0)
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 0, 60, None,
            'Kappa')
        self.mock_whisper.assert_called_once_with('megotsthis',
                                                  StrContains('Kappa', '60'))

    def test_message(self):
        timeout.timeout_user(self.database, self.channel, 'megotsthis',
                             'unittest', message='Kappa')
        self.database.getChatProperties.assert_called_once_with(
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
        self.channel.send.assert_called_once_with('.timeout megotsthis 60', 0)
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 0, 60, 'Kappa',
            None)
        self.assertFalse(self.mock_whisper.called)

    def test_base_level_1(self):
        timeout.timeout_user(self.database, self.channel, 'megotsthis',
                             'unittest', base_level=1)
        self.database.getChatProperties.assert_called_once_with(
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
            '.timeout megotsthis 3600', 0)
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 1, 3600, None, None)
        self.assertFalse(self.mock_whisper.called)

    def test_base_level_2(self):
        timeout.timeout_user(self.database, self.channel, 'megotsthis',
                             'unittest', base_level=2)
        self.database.getChatProperties.assert_called_once_with(
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
            '.timeout megotsthis 86400', 0)
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 2, 86400, None,
            None)
        self.assertFalse(self.mock_whisper.called)

    def test_base_level_3(self):
        timeout.timeout_user(self.database, self.channel, 'megotsthis',
                             'unittest', base_level=3)
        self.database.getChatProperties.assert_called_once_with(
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
            '.timeout megotsthis 86400', 0)
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 2, 86400, None,
            None)
        self.assertFalse(self.mock_whisper.called)

    def test_base_level_negative(self):
        timeout.timeout_user(self.database, self.channel, 'megotsthis',
                             'unittest', base_level=-1)
        self.database.getChatProperties.assert_called_once_with(
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
        self.channel.send.assert_called_once_with('.timeout megotsthis 60', 0)
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 0, 60, None, None)
        self.assertFalse(self.mock_whisper.called)

    def test_override(self):
        self.database.getChatProperties.return_value = {
            'timeoutLength0': 1,
            'timeoutLength1': 1,
            'timeoutLength2': 1,
            }
        timeout.timeout_user(self.database, self.channel, 'megotsthis',
                             'unittest')
        self.database.getChatProperties.assert_called_once_with(
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
        self.channel.send.assert_called_once_with('.timeout megotsthis 1', 0)
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 0, 1, None, None)
        self.assertFalse(self.mock_whisper.called)

    def test_ban(self):
        self.database.getChatProperties.return_value = {
            'timeoutLength0': 0,
            'timeoutLength1': 0,
            'timeoutLength2': 0,
            }
        timeout.timeout_user(self.database, self.channel, 'megotsthis',
                             'unittest')
        self.database.getChatProperties.assert_called_once_with(
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
        self.channel.send.assert_called_once_with('.ban megotsthis', 0)
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 0, 0, None, None)
        self.assertFalse(self.mock_whisper.called)

    def test_repeat_0(self):
        self.channel.sessionData['timeouts'] = {
            'unittest': {
                'megotsthis': (self.now - timedelta(seconds=1), 0)
                }
            }
        timeout.timeout_user(self.database, self.channel, 'megotsthis',
                             'unittest')
        self.database.getChatProperties.assert_called_once_with(
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
            '.timeout megotsthis 3600', 0)
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 1, 3600, None, None)
        self.assertFalse(self.mock_whisper.called)

    def test_repeat_1(self):
        self.channel.sessionData['timeouts'] = {
            'unittest': {
                'megotsthis': (self.now - timedelta(seconds=1), 1)
                }
            }
        timeout.timeout_user(self.database, self.channel, 'megotsthis',
                             'unittest')
        self.database.getChatProperties.assert_called_once_with(
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
            '.timeout megotsthis 86400', 0)
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 2, 86400, None,
            None)
        self.assertFalse(self.mock_whisper.called)

    def test_repeat_2(self):
        self.channel.sessionData['timeouts'] = {
            'unittest': {
                'megotsthis': (self.now - timedelta(seconds=1), 2)
                }
            }
        timeout.timeout_user(self.database, self.channel, 'megotsthis',
                             'unittest')
        self.database.getChatProperties.assert_called_once_with(
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
            '.timeout megotsthis 86400', 0)
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', 2, 86400, None,
            None)
        self.assertFalse(self.mock_whisper.called)


class TestLibraryTimeoutRecord(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'

    def test(self):
        timeout.record_timeout(
            self.database, self.channel, None, 'Kappa', 'Kappa', 'unittest')
        self.assertFalse(self.database.recordTimeout.called)

    def test_timeout(self):
        timeout.record_timeout(
            self.database, self.channel, None,
            '.timeout megotsthis', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, None, 'Kappa',
            None)

    def test_timeout_length(self):
        timeout.record_timeout(
            self.database, self.channel, None,
            '.timeout megotsthis 1', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, 1, 'Kappa',
            None)

    def test_slash_timeout(self):
        timeout.record_timeout(
            self.database, self.channel, None,
            '/timeout megotsthis', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, None, 'Kappa',
            None)

    def test_slash_timeout_length(self):
        timeout.record_timeout(
            self.database, self.channel, None,
            '/timeout megotsthis 1', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, 1, 'Kappa',
            None)

    def test_ban(self):
        timeout.record_timeout(
            self.database, self.channel, None,
            '.ban megotsthis', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, 0, 'Kappa',
            None)

    def test_slash_ban(self):
        timeout.record_timeout(
            self.database, self.channel, None,
            '/ban megotsthis', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', None, 'unittest', None, 0, 'Kappa',
            None)

    def test_bad(self):
        timeout.record_timeout(
            self.database, self.channel, None,
            '.ban', 'Kappa', 'unittest')
        timeout.record_timeout(
            self.database, self.channel, None,
            '.timeout', 'Kappa', 'unittest')
        timeout.record_timeout(
            self.database, self.channel, None,
            '.timeout megotsthis abc', 'Kappa', 'unittest')
        self.assertFalse(self.database.recordTimeout.called)

    def test_who(self):
        timeout.record_timeout(
            self.database, self.channel, 'mebotsthis',
            '.timeout megotsthis', 'Kappa', 'unittest')
        self.database.recordTimeout.assert_called_once_with(
            'botgotsthis', 'megotsthis', 'mebotsthis', 'unittest', None, None,
            'Kappa', None)

    def test_multiple(self):
        timeout.record_timeout(
            self.database, self.channel, None,
            ['.timeout megotsthis 1', '.ban megotsthis'],
            'Kappa', 'unittest')
        self.assertEqual(
            self.database.recordTimeout.mock_calls,
            [call('botgotsthis', 'megotsthis', None, 'unittest', None, 1,
                  'Kappa', None),
             call('botgotsthis', 'megotsthis', None, 'unittest', None, 0,
                  'Kappa', None),
             ])
