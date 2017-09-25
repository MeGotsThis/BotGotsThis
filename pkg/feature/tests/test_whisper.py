from asynctest.mock import patch

import bot.utils
from lib.data.message import Message
from tests.unittest.base_whisper import TestWhisper
from tests.unittest.mock_class import PartialMatch

# Needs to be imported last
from .. import library
from .. import whisper


class TestFeatureWhisper(TestWhisper):
    @patch(library.__name__ + '.feature')
    async def test_feature(self, mock_feature):
        self.assertIs(await whisper.commandFeature(self.args), False)
        self.assertFalse(mock_feature.called)
        mock_feature.return_value = True
        message = Message('!feature feature')
        args = self.args._replace(message=message)
        self.assertIs(await whisper.commandFeature(args), True)
        mock_feature.assert_called_once_with(
            self.database, 'botgotsthis', message,
            PartialMatch(bot.utils.whisper, 'botgotsthis'))
