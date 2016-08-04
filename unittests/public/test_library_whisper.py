import unittest
from bot.twitchmessage import IrcMessageTags
from datetime import datetime
from source.data import WhisperCommandArgs
from source.data.message import Message
from source.data.permissions import WhisperPermissionSet
from source.database import DatabaseBase
from source.public.library import whisper
from unittest.mock import MagicMock, Mock, patch


class TestLibraryWhisper(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.tags = IrcMessageTags()
        self.database = Mock(spec=DatabaseBase)
        self.permissions = MagicMock(spec=WhisperPermissionSet)
        self.args = WhisperCommandArgs(self.database, 'botgotsthis',
                                       Message(''), self.permissions, self.now)

    @patch('bot.utils.whisper', autospec=True)
    def test_send(self, mock_whisper):
        whisper.send('botgotsthis')('Kappa')
        mock_whisper.assert_called_once_with('botgotsthis','Kappa')

    def test_permission(self):
        self.permissions.__getitem__.return_value = True

        @whisper.permission('')
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.permissions.__getitem__.assert_called_once_with('')

    def test_permission_not(self):
        self.permissions.__getitem__.return_value = False

        @whisper.permission('')
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        self.permissions.__getitem__.assert_called_once_with('')

    def test_not_permission(self):
        self.permissions.__getitem__.return_value = False

        @whisper.not_permission('')
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.permissions.__getitem__.assert_called_once_with('')

    def test_not_permission_not(self):
        self.permissions.__getitem__.return_value = True

        @whisper.not_permission('')
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        self.permissions.__getitem__.assert_called_once_with('')

    def test_min_args(self):
        @whisper.min_args(0)
        def t(args):
            return True
        self.assertIs(t(self.args), True)

    def test_min_args_not_enough(self):
        @whisper.min_args(1)
        def t(args):
            return True
        self.assertIs(t(self.args), False)

    def test_min_args_not_return(self):
        @whisper.min_args(1, _return=True)
        def t(args):
            return False
        self.assertIs(t(self.args), True)

    @patch('bot.utils.whisper', autospec=True)
    def test_min_args_not_reason(self, mock_whisper):
        @whisper.min_args(1, reason='Kappa')
        def t(args):
            return False
        t(self.args)
        mock_whisper.assert_called_once_with('botgotsthis', 'Kappa')
