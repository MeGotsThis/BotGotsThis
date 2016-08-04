from source.data.message import Message
from source.public.whisper import feature
from unittest.mock import ANY, patch
from unittests.public.test_whisper import TestWhisper


class TestWhisperFeature(TestWhisper):
    @patch('source.public.library.feature.feature', autospec=True)
    def test_feature(self, mock_feature):
        self.assertIs(feature.commandFeature(self.args), False)
        self.assertFalse(mock_feature.called)
        mock_feature.return_value = True
        message = Message('!feature feature')
        self.assertIs(
            feature.commandFeature(self.args._replace(message=message)), True)
        mock_feature.assert_called_once_with(self.database, 'botgotsthis',
                                             message, ANY)
