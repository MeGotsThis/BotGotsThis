from asynctest.mock import patch

from source.data.message import Message
from tests.unittest.base_channel import TestChannel

# Needs to be imported last
from source.public.channel import feature


class TestChannelFeature(TestChannel):
    @patch('source.public.library.feature.feature')
    async def test_feature(self, mock_feature):
        self.assertIs(await feature.commandFeature(self.args), False)
        self.assertFalse(mock_feature.called)
        mock_feature.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['broadcaster'] = True
        message = Message('!feature feature')
        args = self.args._replace(message=message)
        self.assertIs(await feature.commandFeature(args), True)
        mock_feature.assert_called_once_with(self.database, 'botgotsthis',
                                             message, self.channel.send)
