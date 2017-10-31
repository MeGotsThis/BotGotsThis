from datetime import datetime

import asynctest
from asynctest.mock import MagicMock, Mock, patch

from bot.twitchmessage import IrcMessageTags
from lib.cache import CacheStore
from lib.data import WhisperCommandArgs
from lib.data.message import Message
from lib.data.permissions import WhisperPermissionSet
from lib.database import DatabaseMain
from lib.helper import whisper


class TestLibraryWhisper(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.tags = IrcMessageTags()
        self.data = Mock(spec=CacheStore)
        self.database = Mock(spec=DatabaseMain)
        self.permissions = MagicMock(spec=WhisperPermissionSet)
        self.args = WhisperCommandArgs(
            self.data, self.database, 'botgotsthis', Message(''),
            self.permissions, self.now)

    @asynctest.fail_on(unused_loop=False)
    @patch('bot.utils.whisper', autospec=True)
    def test_send(self, mock_whisper):
        whisper.send('botgotsthis')('Kappa')
        mock_whisper.assert_called_once_with('botgotsthis', 'Kappa')

    async def test_permission(self):
        self.permissions.__getitem__.return_value = True

        @whisper.permission('')
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_permission_not(self):
        self.permissions.__getitem__.return_value = False

        @whisper.permission('')
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_not_permission(self):
        self.permissions.__getitem__.return_value = False

        @whisper.not_permission('')
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_not_permission_not(self):
        self.permissions.__getitem__.return_value = True

        @whisper.not_permission('')
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_min_args(self):
        @whisper.min_args(0)
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)

    async def test_min_args_not_enough(self):
        @whisper.min_args(1)
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)

    async def test_min_args_not_return(self):
        @whisper.min_args(1, _return=True)
        async def t(args):
            return False
        self.assertIs(await t(self.args), True)

    @patch('bot.utils.whisper', autospec=True)
    async def test_min_args_not_reason(self, mock_whisper):
        @whisper.min_args(1, reason='Kappa')
        async def t(args):
            return False
        await t(self.args)
        mock_whisper.assert_called_once_with('botgotsthis', 'Kappa')
