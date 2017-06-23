import bot.utils

from asynctest.mock import patch

from tests.unittest.base_whisper import TestWhisper
from tests.unittest.mock_class import PartialMatch

# Needs to be imported last
from source.public.whisper import broadcaster


class TestWhisperBroadcaster(TestWhisper):
    @patch('source.public.library.broadcaster.come')
    async def test_come(self, mock_come):
        mock_come.return_value = True
        self.assertIs(await broadcaster.commandCome(self.args), True)
        mock_come.assert_called_once_with(
            self.database, 'botgotsthis',
            PartialMatch(bot.utils.whisper, 'botgotsthis'))

    @patch('source.public.library.broadcaster.leave')
    async def test_leave(self, mock_leave):
        mock_leave.return_value = True
        self.assertIs(await broadcaster.commandLeave(self.args), True)
        mock_leave.assert_called_once_with(
            'botgotsthis', PartialMatch(bot.utils.whisper, 'botgotsthis'))

    @patch('source.public.library.broadcaster.empty', autospec=True)
    async def test_empty(self, mock_empty):
        mock_empty.return_value = True
        self.assertIs(await broadcaster.commandEmpty(self.args), True)
        mock_empty.assert_called_once_with(
            'botgotsthis', PartialMatch(bot.utils.whisper, 'botgotsthis'))

    @patch('source.public.library.broadcaster.auto_join')
    async def test_auto_join(self, mock_autojoin):
        mock_autojoin.return_value = True
        self.assertIs(await broadcaster.commandAutoJoin(self.args), True)
        mock_autojoin.assert_called_once_with(
            self.database, 'botgotsthis',
            PartialMatch(bot.utils.whisper, 'botgotsthis'), self.args.message)
