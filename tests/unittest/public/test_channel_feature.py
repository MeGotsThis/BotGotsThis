from source.data.message import Message
from source.public.channel import feature
from tests.unittest.public.test_channel import TestChannel
from unittest.mock import ANY, patch


class TestChannelFeature(TestChannel):
    @patch('source.public.library.feature.feature', autospec=True)
    def test_feature(self, mock_feature):
        self.assertIs(feature.commandFeature(self.args), False)
        self.assertFalse(mock_feature.called)
        mock_feature.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['broadcaster'] = True
        message = Message('!feature feature')
        self.assertIs(
            feature.commandFeature(self.args._replace(message=message)), True)
        mock_feature.assert_called_once_with(self.database, 'botgotsthis',
                                             message, ANY)
