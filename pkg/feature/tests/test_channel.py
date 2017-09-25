from asynctest.mock import patch

from tests.unittest.base_channel import TestChannel
from lib.data.message import Message

# Needs to be imported last
from .. import library
from .. import channel


class TestFeatureChannel(TestChannel):
    @patch(library.__name__ + '.feature')
    async def test_feature(self, mock_feature):
        self.assertIs(await channel.commandFeature(self.args), False)
        self.assertFalse(mock_feature.called)
        mock_feature.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['broadcaster'] = True
        message = Message('!feature feature')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandFeature(args), True)
        mock_feature.assert_called_once_with(self.database, 'botgotsthis',
                                             message, self.channel.send)
