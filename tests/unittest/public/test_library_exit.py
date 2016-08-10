import unittest
from bot.data import Channel
from source.public.library import exit
from tests.unittest.mock_class import StrContains, TypeMatch
from unittest.mock import Mock, patch


def send(messages):
    pass


class TestLibraryExitExit(unittest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.send = Mock(spec=send)

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.channels = {'botgotsthis': self.channel}
        self.mock_globals.running = True

        patcher = patch('bot.utils.partChannel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_part = patcher.start()

        patcher = patch('time.sleep', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_sleep = patcher.start()

    def test(self):
        self.assertIs(exit.exit(self.send), True)
        self.assertIs(self.mock_globals.running, False)
        self.send.assert_called_once_with(StrContains('Goodbye'))
        self.mock_part.assert_called_once_with('botgotsthis')
        self.mock_sleep.assert_called_once_with(TypeMatch(float))
