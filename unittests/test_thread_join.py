import math
import unittest
from bot.data import Channel, Socket
from bot.thread.join import JoinThread
from datetime import datetime, timedelta
from unittest.mock import ANY, Mock, PropertyMock, patch


class TestJoinThread(unittest.TestCase):
    def setUp(self):
        self.join = JoinThread()
        self.socket = Socket('Twitch', 'irc.twitch.tv', 6667)
        self.channel = Channel('botgotsthis', self.socket)
        self.socket._channels[self.channel.channel] = self.channel

        patcher = patch('bot.thread.join.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.clusters = {'Twitch': self.socket}

    @patch('bot.thread.join.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_canProcess(self, mock_now, mock_config):
        mock_config.joinLimit = 5
        mock_now.return_value = datetime(2000, 1, 1)
        self.assertIs(self.join.canProcess, True)

    @patch('bot.thread.join.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_canProcess_partial(self, mock_now, mock_config):
        mock_config.joinLimit = 5
        mock_now.return_value = datetime(2000, 1, 1)
        self.join._joinTimes = ([datetime(2000, 1, 1)] * 4 +
                                [datetime(2000, 1, 1) - timedelta(seconds=20)])
        self.assertIs(self.join.canProcess, True)
        self.assertEqual(self.join._joinTimes, [datetime(2000, 1, 1)] * 4)

    @patch('bot.thread.join.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_canProcess_full(self, mock_now, mock_config):
        mock_config.joinLimit = 5
        mock_now.return_value = datetime(2000, 1, 1)
        self.join._joinTimes = [datetime(2000, 1, 1)] * 5
        self.assertIs(self.join.canProcess, False)
        self.assertEqual(self.join._joinTimes, [datetime(2000, 1, 1)] * 5)

    @patch.object(Socket, 'isConnected', new_callable=PropertyMock)
    def test_connectedChannels(self, mock_isConnected):
        mock_isConnected.return_value = True
        self.assertEquals(self.join.connectedChannels,
                          {'botgotsthis': self.channel})

    @patch.object(Socket, 'isConnected', new_callable=PropertyMock)
    def test_connectedChannels_not_connected(self, mock_isConnected):
        mock_isConnected.return_value = False
        self.assertFalse(self.join.connectedChannels)

    @patch.object(Socket, 'isConnected', new_callable=PropertyMock)
    def test_connectedChannels_multi_sockets(self, mock_isConnected):
        s = Mock(spec=Socket)
        p = PropertyMock(return_value=False)
        type(s).isConnected = p
        c = Channel('megotsthis', self.socket)
        s.channels = {'megotsthis': c}
        self.mock_globals.clusters['mock'] = s
        mock_isConnected.return_value = True
        self.assertEquals(self.join.connectedChannels,
                          {'botgotsthis': self.channel})


    @patch('bot.utils.now', autospec=True)
    def test_connected(self, mock_now):
        mock_now.return_value = datetime(2000, 1, 1)
        self.join.connected(self.socket)
        self.assertIn(datetime(2000, 1, 1), self.join._joinTimes)

    def test_disconnected(self):
        self.join._channelJoined.add(self.channel.channel)
        self.join._channelJoined.add('megotsthis')
        self.join.disconnected(self.socket)
        self.assertTrue(self.join._channelJoined)
        self.assertNotIn(self.channel.channel, self.join._channelJoined)

    def test_onPart(self):
        self.join._channelJoined.add(self.channel.channel)
        self.join._channelJoined.add('megotsthis')
        self.join.onPart(self.channel.channel)
        self.assertTrue(self.join._channelJoined)
        self.assertNotIn(self.channel.channel, self.join._channelJoined)

    @patch('bot.utils.now', autospec=True)
    def test_recordJoin(self, mock_now):
        mock_now.return_value = datetime(2000, 1, 1)
        self.join.recordJoin()
        self.assertIn(datetime(2000, 1, 1), self.join._joinTimes)

    def test_getLowestPriority(self):
        channels = {
            'botgotsthis': Channel('botgotsthis', self.socket, -math.inf),
            'megotsthis': Channel('megotsthis', self.socket, 0),
            'mebotsthis': Channel('mebotsthis', self.socket, math.inf)
            }
        notJoined = set(channels.keys())
        channel = self.join._getJoinWithLowestPriority(channels, notJoined)
        self.assertEqual(channel, 'botgotsthis')
        notJoined.discard(channel)
        channel = self.join._getJoinWithLowestPriority(channels, notJoined)
        self.assertEqual(channel, 'megotsthis')
        notJoined.discard(channel)
        channel = self.join._getJoinWithLowestPriority(channels, notJoined)
        self.assertEqual(channel, 'mebotsthis')
        notJoined.discard(channel)
        self.assertIsNone(
            self.join._getJoinWithLowestPriority(channels, notJoined))

    @patch.object(Socket, 'queueWrite')
    @patch.object(JoinThread, '_getJoinWithLowestPriority')
    @patch.object(JoinThread, 'canProcess', new_callable=PropertyMock)
    @patch.object(JoinThread, 'connectedChannels', new_callable=PropertyMock)
    def test_process_full(self, mock_channels, mock_canProcess,
                          mock_lowPriority, mock_queueWrite):
        mock_canProcess.return_value = False
        self.join.process()
        self.assertFalse(mock_channels.called)
        self.assertFalse(mock_lowPriority.called)
        self.assertFalse(mock_queueWrite.called)
        self.assertFalse(mock_queueWrite.called)

    @patch.object(Socket, 'queueWrite')
    @patch.object(JoinThread, '_getJoinWithLowestPriority')
    @patch.object(JoinThread, 'canProcess', new_callable=PropertyMock)
    @patch.object(JoinThread, 'connectedChannels', new_callable=PropertyMock)
    def test_process_no_channels(self, mock_channels, mock_canProcess,
                                 mock_lowPriority, mock_queueWrite):
        mock_canProcess.return_value = True
        mock_channels.return_value = {}
        self.join.process()
        self.assertFalse(mock_lowPriority.called)
        self.assertFalse(mock_queueWrite.called)

    @patch.object(Socket, 'queueWrite')
    @patch.object(JoinThread, '_getJoinWithLowestPriority')
    @patch.object(JoinThread, 'canProcess', new_callable=PropertyMock)
    @patch.object(JoinThread, 'connectedChannels', new_callable=PropertyMock)
    def test_process_no_to_join(self, mock_channels, mock_canProcess,
                                mock_lowPriority, mock_queueWrite):
        mock_canProcess.return_value = True
        mock_channels.return_value = {'botgotsthis': self.channel}
        self.join._channelJoined.add('botgotsthis')
        self.join.process()
        self.assertFalse(mock_lowPriority.called)
        self.assertFalse(mock_queueWrite.called)

    @patch.object(Socket, 'queueWrite')
    @patch.object(JoinThread, '_getJoinWithLowestPriority')
    @patch.object(JoinThread, 'canProcess', new_callable=PropertyMock)
    @patch.object(JoinThread, 'connectedChannels', new_callable=PropertyMock)
    def test_process(self, mock_channels, mock_canProcess, mock_lowPriority,
                     mock_queueWrite):
        mock_canProcess.return_value = True
        mock_channels.return_value = {'botgotsthis': self.channel}
        mock_lowPriority.return_value = 'botgotsthis'
        self.join.process()
        self.assertTrue(mock_queueWrite.called)
        self.assertEqual(self.join._channelJoined, {'botgotsthis'})
