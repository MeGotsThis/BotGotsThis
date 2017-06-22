import math
import unittest

import bot.coroutine.join

from collections import deque
from datetime import datetime, timedelta

from unittest.mock import Mock, PropertyMock, patch

from bot.data import Channel
from bot.coroutine.connection import ConnectionHandler


class TestJoinManager(unittest.TestCase):
    def setUp(self):
        self.connection = ConnectionHandler('Twitch', 'irc.twitch.tv', 6667)
        self.channel = Channel('botgotsthis', self.connection)
        self.connection._channels[self.channel.channel] = self.channel

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.clusters = {'Twitch': self.connection}

        patcher = patch('bot.coroutine.join._joinTimes')
        self.addCleanup(patcher.stop)
        patcher.start()
        bot.coroutine.join._joinTimes = deque()

        patcher = patch('bot.coroutine.join._channelJoined')
        self.addCleanup(patcher.stop)
        patcher.start()
        bot.coroutine.join._channelJoined = set()

    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_can_process(self, mock_now, mock_config):
        mock_config.joinLimit = 5
        mock_now.return_value = datetime(2000, 1, 1)
        self.assertIs(bot.coroutine.join._can_process(), True)

    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_can_process_partial(self, mock_now, mock_config):
        mock_config.joinLimit = 5
        mock_now.return_value = datetime(2000, 1, 1)
        bot.coroutine.join._joinTimes = deque(
            [datetime(2000, 1, 1) - timedelta(seconds=20)]
            + [datetime(2000, 1, 1)] * 4)
        self.assertIs(bot.coroutine.join._can_process(), True)
        self.assertEqual(list(bot.coroutine.join._joinTimes),
                         [datetime(2000, 1, 1)] * 4)

    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_can_process_full(self, mock_now, mock_config):
        mock_config.joinLimit = 5
        mock_now.return_value = datetime(2000, 1, 1)
        bot.coroutine.join._joinTimes = deque([datetime(2000, 1, 1)] * 5)
        self.assertIs(bot.coroutine.join._can_process(), False)
        self.assertEqual(list(bot.coroutine.join._joinTimes),
                         [datetime(2000, 1, 1)] * 5)

    @patch.object(ConnectionHandler, 'isConnected', new_callable=PropertyMock)
    def test_connected_channels(self, mock_isConnected):
        mock_isConnected.return_value = True
        self.assertEqual(bot.coroutine.join._connected_channels(),
                         {'botgotsthis': self.channel})

    @patch.object(ConnectionHandler, 'isConnected', new_callable=PropertyMock)
    def test_connected_channels_not_connected(self, mock_isConnected):
        mock_isConnected.return_value = False
        self.assertFalse(bot.coroutine.join._connected_channels())

    @patch.object(ConnectionHandler, 'isConnected', new_callable=PropertyMock)
    def test_connected_channels_multi_sockets(self, mock_isConnected):
        s = Mock(spec=ConnectionHandler)
        p = PropertyMock(return_value=False)
        type(s).isConnected = p
        c = Channel('megotsthis', self.connection)
        s.channels = {'megotsthis': c}
        self.mock_globals.clusters['mock'] = s
        mock_isConnected.return_value = True
        self.assertEqual(bot.coroutine.join._connected_channels(),
                         {'botgotsthis': self.channel})

    @patch('bot.utils.now', autospec=True)
    def test_connected(self, mock_now):
        mock_now.return_value = datetime(2000, 1, 1)
        bot.coroutine.join.connected(self.connection)
        self.assertIn(datetime(2000, 1, 1), bot.coroutine.join._joinTimes)

    def test_disconnected(self):
        bot.coroutine.join._channelJoined.add(self.channel.channel)
        bot.coroutine.join._channelJoined.add('megotsthis')
        bot.coroutine.join.disconnected(self.connection)
        self.assertTrue(bot.coroutine.join._channelJoined)
        self.assertNotIn(self.channel.channel,
                         bot.coroutine.join._channelJoined)

    def test_on_part(self):
        bot.coroutine.join._channelJoined.add(self.channel.channel)
        bot.coroutine.join._channelJoined.add('megotsthis')
        bot.coroutine.join.on_part(self.channel.channel)
        self.assertTrue(bot.coroutine.join._channelJoined)
        self.assertNotIn(self.channel.channel,
                         bot.coroutine.join._channelJoined)

    @patch('bot.utils.now', autospec=True)
    def test_record_join(self, mock_now):
        mock_now.return_value = datetime(2000, 1, 1)
        bot.coroutine.join.record_join()
        self.assertIn(datetime(2000, 1, 1), bot.coroutine.join._joinTimes)

    def test_getLowestPriority(self):
        channels = {
            'botgotsthis': Channel('botgotsthis', self.connection, -math.inf),
            'megotsthis': Channel('megotsthis', self.connection, 0),
            'mebotsthis': Channel('mebotsthis', self.connection, math.inf)
            }
        notJoined = set(channels.keys())
        channel = bot.coroutine.join._get_join_with_lowest_priority(channels,
                                                                    notJoined)
        self.assertEqual(channel, 'botgotsthis')
        notJoined.discard(channel)
        channel = bot.coroutine.join._get_join_with_lowest_priority(channels,
                                                                    notJoined)
        self.assertEqual(channel, 'megotsthis')
        notJoined.discard(channel)
        channel = bot.coroutine.join._get_join_with_lowest_priority(channels,
                                                                    notJoined)
        self.assertEqual(channel, 'mebotsthis')
        notJoined.discard(channel)
        self.assertIsNone(
            bot.coroutine.join._get_join_with_lowest_priority(channels,
                                                              notJoined))

    @patch.object(ConnectionHandler, 'queue_write')
    @patch('bot.coroutine.join._get_join_with_lowest_priority')
    @patch('bot.coroutine.join._can_process')
    @patch('bot.coroutine.join._connected_channels')
    def test_join_full(self, mock_channels, mock_canProcess,
                          mock_lowPriority, mock_queue_write):
        mock_canProcess.return_value = False
        bot.coroutine.join.join_a_channel()
        self.assertFalse(mock_channels.called)
        self.assertFalse(mock_lowPriority.called)
        self.assertFalse(mock_queue_write.called)
        self.assertFalse(mock_queue_write.called)

    @patch.object(ConnectionHandler, 'queue_write')
    @patch('bot.coroutine.join._get_join_with_lowest_priority')
    @patch('bot.coroutine.join._can_process')
    @patch('bot.coroutine.join._connected_channels')
    def test_join_no_channels(self, mock_channels, mock_canProcess,
                                 mock_lowPriority, mock_queue_write):
        mock_canProcess.return_value = True
        mock_channels.return_value = {}
        bot.coroutine.join.join_a_channel()
        self.assertFalse(mock_lowPriority.called)
        self.assertFalse(mock_queue_write.called)

    @patch.object(ConnectionHandler, 'queue_write')
    @patch('bot.coroutine.join._get_join_with_lowest_priority')
    @patch('bot.coroutine.join._can_process')
    @patch('bot.coroutine.join._connected_channels')
    def test_join_no_to_join(self, mock_channels, mock_canProcess,
                                mock_lowPriority, mock_queue_write):
        mock_canProcess.return_value = True
        mock_channels.return_value = {'botgotsthis': self.channel}
        bot.coroutine.join._channelJoined.add('botgotsthis')
        bot.coroutine.join.join_a_channel()
        self.assertFalse(mock_lowPriority.called)
        self.assertFalse(mock_queue_write.called)

    @patch.object(ConnectionHandler, 'queue_write')
    @patch('bot.coroutine.join._get_join_with_lowest_priority')
    @patch('bot.coroutine.join._can_process')
    @patch('bot.coroutine.join._connected_channels')
    def test_join(self, mock_channels, mock_canProcess, mock_lowPriority,
                  mock_queue_write):
        mock_canProcess.return_value = True
        mock_channels.return_value = {'botgotsthis': self.channel}
        mock_lowPriority.return_value = 'botgotsthis'
        bot.coroutine.join.join_a_channel()
        self.assertTrue(mock_queue_write.called)
        self.assertEqual(bot.coroutine.join._channelJoined, {'botgotsthis'})
