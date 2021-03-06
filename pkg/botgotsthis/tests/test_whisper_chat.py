import bot.utils

from asynctest.mock import patch

from tests.unittest.base_whisper import TestWhisper
from tests.unittest.mock_class import PartialMatch

# Needs to be imported last
from ..library import chat as library_chat
from ..whisper import chat


class TestWhisperBroadcaster(TestWhisper):
    @patch(library_chat.__name__ + '.empty', autospec=True)
    async def test_empty(self, mock_empty):
        mock_empty.return_value = True
        self.assertIs(await chat.commandEmpty(self.args), True)
        mock_empty.assert_called_once_with(
            'botgotsthis', PartialMatch(bot.utils.whisper, 'botgotsthis'))
