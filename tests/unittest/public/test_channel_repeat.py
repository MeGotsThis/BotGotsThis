import unittest
from bot.data import Channel
from datetime import datetime, timedelta
from source.data.message import Message
from source.database import DatabaseBase
from source.public.channel import repeat
from tests.unittest.public.test_channel import TestChannel
from unittest.mock import Mock, patch


class TestChannelRepeat(TestChannel):
    @patch('source.public.channel.repeat.process_auto_repeat', autospec=True)
    def test_auto_repeat(self, mock_process):
        self.assertIs(repeat.commandAutoRepeat(self.args), False)
        self.assertFalse(mock_process.called)
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        self.assertIs(repeat.commandAutoRepeat(self.args), True)
        mock_process.assert_called_once_with(self.args, None)

    @patch('source.public.channel.repeat.process_auto_repeat', autospec=True)
    def test_auto_repeat_count(self, mock_process):
        self.assertIs(repeat.commandAutoRepeatCount(self.args), False)
        self.assertFalse(mock_process.called)
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        self.assertIs(repeat.commandAutoRepeat(self.args), True)
        mock_process.assert_called_once_with(self.args, None)

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_false(self, mock_thread):
        self.assertIs(repeat.process_auto_repeat(self.args, None), False)
        self.assertFalse(mock_thread.called)

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_error(self, mock_thread):
        self.args = self.args._replace(message=Message('!autorepeat abc'))
        self.assertIs(repeat.process_auto_repeat(self.args, None), False)
        self.assertNotIn('repeatThread', self.channel.sessionData)
        self.assertFalse(mock_thread.called)

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_off(self, mock_thread):
        self.args = self.args._replace(message=Message('!autorepeat off abc'))
        self.assertIs(repeat.process_auto_repeat(self.args, None), True)
        self.assertNotIn('repeatThread', self.channel.sessionData)
        self.assertFalse(mock_thread.called)

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_zero_minutes(self, mock_thread):
        self.args = self.args._replace(message=Message('!autorepeat 0 abc'))
        self.assertIs(repeat.process_auto_repeat(self.args, None), True)
        self.assertNotIn('repeatThread', self.channel.sessionData)
        self.assertFalse(mock_thread.called)

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_zero_count(self, mock_thread):
        self.args = self.args._replace(message=Message('!autorepeat 1 abc'))
        self.assertIs(repeat.process_auto_repeat(self.args, 0), True)
        self.assertNotIn('repeatThread', self.channel.sessionData)
        self.assertFalse(mock_thread.called)

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_no_message(self, mock_thread):
        self.args = self.args._replace(message=Message('!autorepeat 1'))
        self.assertIs(repeat.process_auto_repeat(self.args, None), True)
        self.assertNotIn('repeatThread', self.channel.sessionData)
        self.assertFalse(mock_thread.called)

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process(self, mock_thread):
        self.args = self.args._replace(message=Message('!autorepeat 1 Kappa'))
        self.assertIs(repeat.process_auto_repeat(self.args, None), True)
        mock_thread.assert_called_once_with(
            chat=self.channel, message='Kappa', duration=timedelta(minutes=1),
            count=None)
        self.assertIn('repeatThread', self.channel.sessionData)
        thread = self.channel.sessionData['repeatThread']
        thread.start.assert_called_once_with()

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_count(self, mock_thread):
        self.args = self.args._replace(message=Message('!autorepeat 1 Kappa'))
        self.assertIs(repeat.process_auto_repeat(self.args, 1), True)
        mock_thread.assert_called_once_with(
            chat=self.channel, message='Kappa', duration=timedelta(minutes=1),
            count=1)
        self.assertIn('repeatThread', self.channel.sessionData)
        thread = self.channel.sessionData['repeatThread']
        thread.start.assert_called_once_with()

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_off_with_thread(self, mock_thread):
        thread = Mock(spec=repeat.MessageRepeater)
        self.channel.sessionData['repeatThread'] = thread
        self.args = self.args._replace(message=Message('!autorepeat off abc'))
        self.assertIs(repeat.process_auto_repeat(self.args, None), True)
        self.assertIn('repeatThread', self.channel.sessionData)
        self.assertFalse(mock_thread.called)
        self.assertEqual(thread.count, 0)

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_zero_duration_with_thread(self, mock_thread):
        thread = Mock(spec=repeat.MessageRepeater)
        self.channel.sessionData['repeatThread'] = thread
        self.args = self.args._replace(message=Message('!autorepeat 0 abc'))
        self.assertIs(repeat.process_auto_repeat(self.args, None), True)
        self.assertIn('repeatThread', self.channel.sessionData)
        self.assertFalse(mock_thread.called)
        self.assertEqual(thread.count, 0)

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_zero_count_with_thread(self, mock_thread):
        thread = Mock(spec=repeat.MessageRepeater)
        self.channel.sessionData['repeatThread'] = thread
        self.args = self.args._replace(message=Message('!autorepeat 1 abc'))
        self.assertIs(repeat.process_auto_repeat(self.args, 0), True)
        self.assertIn('repeatThread', self.channel.sessionData)
        self.assertFalse(mock_thread.called)
        self.assertEqual(thread.count, 0)

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_no_message_with_thread(self, mock_thread):
        thread = Mock(spec=repeat.MessageRepeater)
        self.channel.sessionData['repeatThread'] = thread
        self.args = self.args._replace(message=Message('!autorepeat 1'))
        self.assertIs(repeat.process_auto_repeat(self.args, None), True)
        self.assertIn('repeatThread', self.channel.sessionData)
        self.assertFalse(mock_thread.called)
        self.assertEqual(thread.count, 0)

    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_with_thread(self, mock_thread):
        thread = Mock(spec=repeat.MessageRepeater)
        self.channel.sessionData['repeatThread'] = thread
        self.args = self.args._replace(message=Message('!autorepeat 1 Kappa'))
        self.assertIs(repeat.process_auto_repeat(self.args, None), True)
        mock_thread.assert_called_once_with(
            chat=self.channel, message='Kappa', duration=timedelta(minutes=1),
            count=None)
        self.assertIn('repeatThread', self.channel.sessionData)
        thread_ = self.channel.sessionData['repeatThread']
        thread_.start.assert_called_once_with()
        self.assertIsNot(self.channel.sessionData['repeatThread'], thread)
        
    @patch('source.public.channel.repeat.MessageRepeater', autospec=True)
    def test_process_count_with_thread(self, mock_thread):
        thread = Mock(spec=repeat.MessageRepeater)
        self.channel.sessionData['repeatThread'] = thread
        self.args = self.args._replace(message=Message('!autorepeat 1 Kappa'))
        self.assertIs(repeat.process_auto_repeat(self.args, 1), True)
        mock_thread.assert_called_once_with(
            chat=self.channel, message='Kappa', duration=timedelta(minutes=1),
            count=1)
        self.assertIn('repeatThread', self.channel.sessionData)
        thread_ = self.channel.sessionData['repeatThread']
        thread_.start.assert_called_once_with()
        self.assertIsNot(self.channel.sessionData['repeatThread'], thread)


class TestChannelRepeatMessageRepeater(unittest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.isMod = False
        self.repeater = repeat.MessageRepeater(
            chat=self.channel, message='Kappa', duration=timedelta(minutes=5))
        self.channel.sessionData = {'repeatThread': self.repeater}

    def test_count(self):
        self.assertIsNone(self.repeater.count)
        self.repeater.count = 0
        self.assertEqual(self.repeater.count, 0)
        self.repeater.count = None
        self.assertIsNone(self.repeater.count)

    @patch('bot.globals', autospec=True)
    def test_running(self, mock_globals):
        mock_globals.running = True
        self.assertIs(self.repeater.running, True)

    @patch('bot.globals', autospec=True)
    def test_running_zero_count(self, mock_globals):
        mock_globals.running = True
        self.repeater.count = 0
        self.assertIs(self.repeater.running, False)

    @patch('bot.globals', autospec=True)
    def test_running_zero_count(self, mock_globals):
        mock_globals.running = True
        self.repeater.count = 1
        self.assertIs(self.repeater.running, True)

    @patch('bot.globals', autospec=True)
    def test_running_not_running(self, mock_globals):
        mock_globals.running = False
        self.assertIs(self.repeater.running, False)

    @patch('bot.globals', autospec=True)
    def test_running_zero_count_not_running(self, mock_globals):
        mock_globals.running = True
        self.repeater.count = 0
        self.assertIs(self.repeater.running, False)

    @patch('bot.globals', autospec=True)
    def test_running_zero_count_not_running(self, mock_globals):
        mock_globals.running = False
        self.repeater.count = 1
        self.assertIs(self.repeater.running, False)

    @patch('bot.utils.now', autospec=True)
    @patch('source.database.factory.getDatabase', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process(self, mock_record, mock_database, mock_now):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        self.repeater._lastTime = now - timedelta(minutes=5)
        self.repeater.process()
        mock_now.assert_called_once_with()
        self.channel.send.assert_called_once_with('Kappa')
        self.assertFalse(mock_database.called)
        self.assertFalse(mock_record.called)

    @patch('bot.utils.now', autospec=True)
    @patch('source.database.factory.getDatabase', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process_recent(self, mock_record, mock_database, mock_now):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        self.repeater._lastTime = now
        self.repeater.process()
        mock_now.assert_called_once_with()
        self.assertFalse(self.channel.send.called)
        self.assertFalse(mock_database.called)
        self.assertFalse(mock_record.called)

    @patch('bot.utils.now', autospec=True)
    @patch('source.database.factory.getDatabase', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process_chat_mod(self, mock_record, mock_database, mock_now):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        database = Mock(spec=DatabaseBase)
        mock_database.return_value.__enter__.return_value = database
        self.channel.isMod = True
        self.repeater._lastTime = now - timedelta(minutes=5)
        self.repeater.process()
        mock_now.assert_called_once_with()
        self.channel.send.assert_called_once_with('Kappa')
        mock_database.assert_called_once_with()
        mock_record.assert_called_once_with(database, self.channel, None,
                                            'Kappa', None, 'autorepeat')

    def test_end(self):
        self.repeater.end()
        self.assertNotIn('repeatThread', self.channel.sessionData)

    def test_end_another_thread(self):
        repeater = repeat.MessageRepeater(chat=self.channel)
        self.channel.sessionData['repeatThread'] = repeater
        self.repeater.end()
        self.assertIn('repeatThread', self.channel.sessionData)
        self.assertIsNot(
            self.channel.sessionData['repeatThread'], self.repeater)
