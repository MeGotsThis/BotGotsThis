import bot.utils

from asynctest.mock import patch

from tests.unittest.base_whisper import TestWhisper
from tests.unittest.mock_class import PartialMatch

# Needs to be imported last
from .. import library
from .. import whisper


class TestWhisperBroadcaster(TestWhisper):
    @patch(library.__name__ + '.come')
    async def test_come(self, mock_come):
        mock_come.return_value = True
        self.assertIs(await whisper.commandCome(self.args), True)
        mock_come.assert_called_once_with(
            self.database, 'botgotsthis',
            PartialMatch(bot.utils.whisper, 'botgotsthis'))

    @patch(library.__name__ + '.leave')
    async def test_leave(self, mock_leave):
        mock_leave.return_value = True
        self.assertIs(await whisper.commandLeave(self.args), True)
        mock_leave.assert_called_once_with(
            'botgotsthis', PartialMatch(bot.utils.whisper, 'botgotsthis'))

    @patch(library.__name__ + '.auto_join')
    async def test_auto_join(self, mock_autojoin):
        mock_autojoin.return_value = True
        self.assertIs(await whisper.commandAutoJoin(self.args), True)
        mock_autojoin.assert_called_once_with(
            self.database, 'botgotsthis',
            PartialMatch(bot.utils.whisper, 'botgotsthis'), self.args.message)
