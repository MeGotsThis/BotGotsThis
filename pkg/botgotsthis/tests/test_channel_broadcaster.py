from asynctest.mock import patch

from tests.unittest.base_channel import TestChannel

# Needs to be imported last
from pkg.botgotsthis.channel import broadcaster


class TestChannelBroadcaster(TestChannel):
    @patch('pkg.botgotsthis.library.broadcaster.empty')
    async def test_empty(self, mock_empty):
        self.assertIs(await broadcaster.commandEmpty(self.args), False)
        self.assertFalse(mock_empty.called)
        mock_empty.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(await broadcaster.commandEmpty(self.args), True)
        mock_empty.assert_called_once_with('botgotsthis', self.channel.send)

    @patch('pkg.botgotsthis.library.broadcaster.set_timeout_level')
    async def test_set_timeout_level(self, mock_set_timeout):
        self.assertIs(await broadcaster.commandSetTimeoutLevel(self.args),
                      False)
        self.assertFalse(mock_set_timeout.called)
        mock_set_timeout.return_value = True
        self.permissionSet['broadcaster'] = True
        self.assertIs(await broadcaster.commandSetTimeoutLevel(self.args),
                      True)
        mock_set_timeout.assert_called_once_with(
            self.database, 'botgotsthis', self.channel.send, self.args.message)
