import unittest
from bot.thread.logging import Logging
from unittest.mock import mock_open, patch


class TestLogging(unittest.TestCase):
    def setUp(self):
        self.logging = Logging()

    def test_log(self):
        self.logging.log('log', 'Kappa')
        self.assertEqual(self.logging.queue.get(), ('log', 'Kappa'))

    @patch('builtins.open', new_callable=mock_open)
    def test_runTasks(self, mockopen):
        self.logging.queue.put(('log', 'Kappa'))
        self.logging.process()
        self.assertTrue(mockopen.called)
        self.assertTrue(mockopen().write.called)
