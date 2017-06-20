from asynctest.mock import patch

import bot.utils
from source.data.message import Message
from tests.unittest.base_whisper import TestWhisper
from tests.unittest.mock_class import PartialMatch

# Needs to be imported last
from source.public.whisper import feature


class TestWhisperFeature(TestWhisper):
    @patch('source.public.library.feature.feature')
    async def test_feature(self, mock_feature):
        self.assertIs(await feature.commandFeature(self.args), False)
        self.assertFalse(mock_feature.called)
        mock_feature.return_value = True
        message = Message('!feature feature')
        args = self.args._replace(message=message)
        self.assertIs(await feature.commandFeature(args), True)
        mock_feature.assert_called_once_with(
            self.database, 'botgotsthis', message,
            PartialMatch(bot.utils.whisper, 'botgotsthis'))
