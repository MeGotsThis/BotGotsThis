import asyncio
import unittest

import asynctest

from datetime import datetime, timedelta
from io import StringIO

from asynctest.mock import Mock, patch

from bot.coroutine import connection
from bot.data import Channel, ChatMessage, MessagingQueue
from bot.data import WhisperMessage
from bot.data.error import ConnectionReset, LoginUnsuccessful
from bot.twitchmessage import IrcMessage


class TestConnectionHandler(unittest.TestCase):
    def setUp(self):
        self.connection = connection.ConnectionHandler(
            'Kappa', 'irc.twitch.tv', 6667)
        self.channel = Channel('botgotsthis', self.connection)
        self.whisper = WhisperMessage('botgotsthis', 'Kappa')

    def test_name(self):
        self.assertEqual(self.connection.name, 'Kappa')

    def test_server(self):
        self.assertEqual(self.connection.server, 'irc.twitch.tv')

    def test_port(self):
        self.assertEqual(self.connection.port, 6667)

    def test_address(self):
        self.assertEqual(self.connection.address, ('irc.twitch.tv', 6667))

    def test_isConnected(self):
        self.assertIs(self.connection.isConnected, False)

    def test_channels(self):
        self.assertEqual(self.connection.channels, {})

    def test_messaging(self):
        self.assertIsInstance(self.connection.messaging, MessagingQueue)

    def test_writeQueue(self):
        self.assertFalse(self.connection.writeQueue, MessagingQueue)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.coroutine.join.record_join', autospec=True)
    @patch.object(Channel, 'onJoin', autospec=True)
    def test_on_write_join(self, mock_onJoin, mock_record_join, mock_stdout):
        now = datetime(2000, 1, 1)
        message = IrcMessage(None, None, 'JOIN')
        self.connection._on_write(message, now, channel=self.channel)
        mock_onJoin.assert_called_once_with(self.channel)
        mock_record_join.assert_called_once_with()
        self.assertNotEqual(mock_stdout.getvalue(), '')

    def test_on_write_ping(self):
        now = datetime(2000, 1, 1)
        message = IrcMessage(None, None, 'PING')
        self.connection._on_write(message, now, channel=self.channel)
        self.assertEqual(self.connection.lastSentPing, now)

    @patch.object(connection.ConnectionHandler, 'queue_write', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_ping(self, mock_now, mock_queue_write):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        self.connection.ping()
        self.assertIs(mock_queue_write.called, True)
        self.assertTrue(any(m for m in mock_queue_write.call_args_list
                            if m[0][1].command == 'PONG'))
        self.assertEqual(self.connection.lastPing, now)

    @patch.object(connection.ConnectionHandler, 'disconnect', autospec=True)
    @patch.object(connection.ConnectionHandler, 'queue_write', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_send_ping_tooSoon(self, mock_now, mock_queue_write,
                               mock_disconnect):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        self.connection.lastSentPing = now
        self.connection.lastPing = now
        self.connection.send_ping()
        self.assertFalse(mock_disconnect.called)
        self.assertFalse(mock_queue_write.called)

    @patch.object(connection.ConnectionHandler, 'disconnect', autospec=True)
    @patch.object(connection.ConnectionHandler, 'queue_write', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_send_ping(self, mock_now, mock_config, queue_write,
                       mock_disconnect):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_config.botnick = 'botgotsthis'
        self.connection.lastSentPing = now - timedelta(minutes=1, seconds=1)
        self.connection.lastPing = now
        self.connection.send_ping()
        self.assertFalse(mock_disconnect.called)
        self.assertIs(queue_write.called, True)
        self.assertTrue(any(m for m in queue_write.call_args_list
                            if m[0][1].command == 'PING'))

    @patch.object(connection.ConnectionHandler, 'queue_write', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_send_ping_noresponse(self, mock_now, mock_config, queue_write):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_config.botnick = 'botgotsthis'
        self.connection.lastSentPing = now
        self.connection.lastPing = now - timedelta(minutes=2)
        self.assertRaises(ConnectionError, self.connection.send_ping)
        self.assertFalse(queue_write.called)

    @patch.object(connection.ConnectionHandler, 'disconnect', autospec=True)
    @patch.object(connection.ConnectionHandler, 'queue_write', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_send_ping_noresponse_late(self, mock_now, mock_config,
                                       queue_write, mock_disconnect):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_config.botnick = 'botgotsthis'
        self.connection.lastSentPing = now - timedelta(minutes=1, seconds=1)
        self.connection.lastPing = now - timedelta(minutes=2)
        self.connection.send_ping()
        self.assertFalse(mock_disconnect.called)
        self.assertIs(queue_write.called, True)
        self.assertTrue(any(m for m in queue_write.call_args_list
                            if m[0][1].command == 'PING'))

    @patch('bot.config', autospec=True)
    @patch('bot.utils.logIrcMessage', autospec=True)
    def test_log_read(self, mock_logIrcMessage, mock_config):
        mock_config.botnick = 'botgotsthis'
        self.connection._log_read('')
        self.assertTrue(mock_logIrcMessage.called)

    @patch('bot.config', autospec=True)
    @patch('bot.utils.logIrcMessage', autospec=True)
    def test_log_write(self, mock_logIrcMessage, mock_config):
        mock_config.botnick = 'botgotsthis'
        self.connection._log_write(IrcMessage(None, None, 1))
        self.assertTrue(mock_logIrcMessage.called)

    @patch('bot.config', autospec=True)
    @patch('bot.utils.logIrcMessage', autospec=True)
    def test_log_write_channel(self, mock_logIrcMessage, mock_config):
        mock_config.botnick = 'botgotsthis'
        message = IrcMessage(None, None, 1)
        self.connection._log_write(message, channel=self.channel)
        self.assertEqual(mock_logIrcMessage.call_count, 2)

    @patch('bot.config', autospec=True)
    @patch('bot.utils.logIrcMessage', autospec=True)
    def test_log_write_whisper(self, mock_logIrcMessage, mock_config):
        mock_config.botnick = 'botgotsthis'
        message = IrcMessage(None, None, 1)
        self.connection._log_write(message, whisper=self.whisper)
        self.assertEqual(mock_logIrcMessage.call_count, 4)

    @patch('bot.config', autospec=True)
    @patch('bot.utils.logIrcMessage', autospec=True)
    def test_log_write_channel_whisper(self, mock_logIrcMessage, mock_config):
        mock_config.botnick = 'botgotsthis'
        self.assertRaises(ValueError, self.connection._log_write,
                          IrcMessage(None, None, 1),
                          channel=self.channel, whisper=self.whisper)
        self.assertEqual(mock_logIrcMessage.call_count, 1)

    def test_queueWrite_none(self):
        self.assertRaises(TypeError, self.connection.queue_write, None)

    def test_queueWrite_channel_int(self):
        self.assertRaises(TypeError, self.connection.queue_write,
                          IrcMessage(None, None, 1), channel=1)

    def test_queueWrite_whisper_int(self):
        self.assertRaises(TypeError, self.connection.queue_write,
                          IrcMessage(None, None, 1), whisper=1)

    def test_queueWrite_channel_whisper(self):
        self.assertRaises(ValueError, self.connection.queue_write,
                          IrcMessage(None, None, 1),
                          channel=self.channel,
                          whisper=self.whisper)

    def test_queueWrite(self):
        message = IrcMessage(None, None, 1)
        self.connection.queue_write(message)
        self.assertEqual(len(self.connection.writeQueue), 1)
        self.assertEqual(self.connection.writeQueue[0][0], (message,))
        self.assertEqual(self.connection.writeQueue[0][1], {})

    def test_queueWrite_channel(self):
        message = IrcMessage(None, None, 1)
        self.connection.queue_write(message, channel=self.channel)
        self.assertEqual(len(self.connection.writeQueue), 1)
        self.assertEqual(self.connection.writeQueue[0][0], (message,))
        self.assertEqual(self.connection.writeQueue[0][1],
                         {'channel': self.channel})

    def test_queueWrite_whisper(self):
        message = IrcMessage(None, None, 1)
        self.connection.queue_write(message, whisper=self.whisper)
        self.assertEqual(len(self.connection.writeQueue), 1)
        self.assertEqual(self.connection.writeQueue[0][0], (message,))
        self.assertEqual(self.connection.writeQueue[0][1],
                         {'whisper': self.whisper})

    def test_queueWrite_multi(self):
        message1 = IrcMessage(None, None, 1)
        message2 = IrcMessage(None, None, 2)
        self.connection.queue_write(message1)
        self.connection.queue_write(message2)
        self.assertEqual(len(self.connection.writeQueue), 2)
        self.assertEqual(self.connection.writeQueue[0][0], (message1,))
        self.assertEqual(self.connection.writeQueue[1][0], (message2,))

    def test_queueWrite_multi_prepend(self):
        message1 = IrcMessage(None, None, 1)
        message2 = IrcMessage(None, None, 2)
        self.connection.queue_write(message1)
        self.connection.queue_write(message2, prepend=True)
        self.assertEqual(len(self.connection.writeQueue), 2)
        self.assertEqual(self.connection.writeQueue[0][0], (message2,))
        self.assertEqual(self.connection.writeQueue[1][0], (message1,))

    def test_join_channel(self):
        self.connection.join_channel(self.channel)
        self.assertIn(self.channel.channel, self.connection._channels)
        self.assertIs(self.connection._channels[self.channel.channel],
                      self.channel)

    @patch('bot.globals', autospec=True)
    @patch.object(connection.ConnectionHandler, 'queue_write', autospec=True)
    def test_part_channel(self, mock_queue_write, mock_globals):
        self.connection.part_channel(self.channel)
        self.assertNotIn(self.channel.channel, self.connection._channels)
        self.assertFalse(mock_queue_write.called)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.coroutine.join.on_part', autospec=True)
    @patch.object(connection.ConnectionHandler, 'queue_write', autospec=True)
    def test_part_channel_contains(self, mock_queue_write, mock_on_part,
                                   mock_stdout):
        self.connection._channels[self.channel.channel] = self.channel
        self.connection.part_channel(self.channel)
        self.assertNotIn(self.channel.channel, self.connection._channels)
        self.assertTrue(mock_queue_write.called)
        self.assertTrue(mock_on_part.called)
        self.assertTrue(any(m for m in mock_queue_write.call_args_list
                            if m[0][1].command == 'PART'))
        self.assertNotEqual(mock_stdout.getvalue(), '')

    @patch('bot.globals', autospec=True)
    @patch.object(MessagingQueue, 'popChat', autospec=True)
    @patch.object(MessagingQueue, 'popWhisper', autospec=True)
    @patch.object(connection.ConnectionHandler, 'queue_write', autospec=True)
    def test_flush_writes(self, mock_queue_write, mock_popWhisper,
                          mock_popChat, mock_globals):
        mock_globals.groupChannel = self.channel
        mock_popWhisper.side_effect = [
            WhisperMessage('botgotsthis', 'Kappa'),
            WhisperMessage('megotsthis', 'KappaPride'),
            None]
        mock_popChat.side_effect = [
            ChatMessage(self.channel, 'KappaRoss'),
            ChatMessage(self.channel, 'KappaClaus'),
            None]
        self.connection.flush_writes()
        self.assertEqual(mock_queue_write.call_count, 4)
        self.assertTrue(len([m for m in mock_queue_write.call_args_list
                             if m[0][1].command == 'PRIVMSG']), 4)
        self.assertTrue(len([m for m in mock_queue_write.call_args_list
                             if 'channel' in m[1]
                             and m[1]['channel'] is self.channel]), 2)
        self.assertTrue(len([m for m in mock_queue_write.call_args_list
                             if 'whisper' in m[1]
                             and m[1]['whisper'].nick in ['megotsthis',
                                                          'botgotsthis']]), 2)


class TestConnectionHandlerAsync(asynctest.TestCase):
    def setUp(self):
        self.connection = connection.ConnectionHandler(
            'Kappa', 'irc.twitch.tv', 6667)
        self.channel = Channel('botgotsthis', self.connection)
        self.whisper = WhisperMessage('botgotsthis', 'Kappa')

        self.mock_transport = Mock(spec=asyncio.Transport)
        self.mock_reader = Mock(asyncio.StreamReader)
        self.mock_writer = Mock(asyncio.StreamWriter)
        self.mock_writer.transort = self.mock_transport

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.coroutine.join.connected', autospec=True)
    @patch('asyncio.open_connection')
    @patch.object(connection.ConnectionHandler, 'login')
    async def test_connect(self, mock_login, mock_connect, mock_connected,
                           mock_now, mock_stdout):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_connect.return_value = self.mock_reader, self.mock_writer
        await self.connection.connect()
        mock_connect.assert_any_call('irc.twitch.tv', 6667)
        mock_connected.assert_called_with(self.connection)
        self.assertNotEqual(mock_stdout.getvalue(), '')
        mock_login.assert_called_once_with(self.mock_writer)
        self.assertEqual(self.connection.lastSentPing, now)
        self.assertEqual(self.connection.lastPing, now)
        self.assertEqual(self.connection.lastConnectAttempt, now)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.coroutine.join.connected', autospec=True)
    @patch('asyncio.open_connection')
    @patch.object(connection.ConnectionHandler, 'login')
    async def test_connect_throttle(self, mock_login, mock_connect,
                                    mock_connected, mock_now, mock_stdout):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        self.connection.lastConnectAttempt = now
        await self.connection.connect()
        mock_connect.assert_not_called()
        mock_connected.assert_not_called()
        self.assertEqual(mock_stdout.getvalue(), '')
        self.assertFalse(mock_login.called)
        self.assertEqual(self.connection.lastSentPing, datetime.max)
        self.assertEqual(self.connection.lastPing, datetime.max)
        self.assertEqual(self.connection.lastConnectAttempt, now)

    async def test_login_none(self):
        with self.assertRaises(TypeError):
            await self.connection.login(None)

    @patch('bot.config', autospec=True)
    @patch.object(connection.ConnectionHandler, '_log_write')
    async def test_login(self, mock_log_write, mock_config):
        writer = Mock(spec=asyncio.StreamWriter)
        mock_config.botnick = 'botgotsthis'
        mock_config.password = 'oauth:some_long_oauth_token_here'
        await self.connection.login(writer)
        self.assertGreaterEqual(writer.write.call_count, 3)
        self.assertEqual(writer.write.call_count, mock_log_write.call_count)
        self.assertTrue(writer.drain.called)

    @asynctest.fail_on(unused_loop=False)
    def test_disconnect(self):
        with self.assertRaises(ConnectionError):
            self.connection.disconnect()

    async def test_write_none(self):
        with self.assertRaises(TypeError):
            await self.connection.write(None)

    async def test_write(self):
        with self.assertRaises(ConnectionError):
            await self.connection.write(IrcMessage(None, None, 'PING'))

    @patch.object(connection.ConnectionHandler, 'write', autospec=True)
    async def test_drain(self, mock_write):
        with self.assertRaises(ConnectionError):
            await self.connection.drain()
        self.assertFalse(mock_write.called)

    async def test_read(self):
        with self.assertRaises(ConnectionError):
            await self.connection.read()


class TestConnectionConnected(asynctest.TestCase):
    async def setUp(self):
        self.connection = connection.ConnectionHandler(
            'Kappa', 'irc.twitch.tv', 6667)
        self.channel = Channel('botgotsthis', self.connection)
        self.whisper = WhisperMessage('botgotsthis', 'Kappa')

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.botnick = 'botgotsthis'

        patcher = patch('bot.utils.now', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_now = patcher.start()
        self.now = datetime(2000, 1, 1, 0, 0, 0)
        self.mock_now.return_value = self.now

        patcher = patch('bot.coroutine.join.disconnected')
        self.addCleanup(patcher.stop)
        self.mock_disconnected = patcher.start()

        with patch('asyncio.open_connection') as mock_connection,\
                patch('sys.stdout', new_callable=StringIO),\
                patch.object(connection.ConnectionHandler, 'login'):
            self.mock_transport = Mock(spec=asyncio.Transport)
            self.mock_reader = Mock(asyncio.StreamReader)
            self.mock_writer = Mock(asyncio.StreamWriter)
            self.mock_writer.transport = self.mock_transport
            mock_connection.return_value = self.mock_reader, self.mock_writer
            await self.connection.connect()

    async def test_connect(self):
        with self.assertRaises(ConnectionError):
            await self.connection.connect()

    @asynctest.fail_on(unused_loop=False)
    @patch('sys.stdout', new_callable=StringIO)
    def test_disconnect(self, mock_close):
        self.connection.disconnect()
        self.assertIsNone(self.connection._transport)
        self.assertIsNone(self.connection._reader)
        self.assertIsNone(self.connection._writer)
        self.assertTrue(self.mock_transport.close.called)
        self.assertTrue(self.mock_disconnected.called)
        self.assertEqual(self.connection.lastConnectAttempt, self.now)
        self.assertEqual(self.connection.lastPing, datetime.max)
        self.assertEqual(self.connection.lastSentPing, datetime.max)

    @patch.object(connection.ConnectionHandler, 'write')
    async def test_drain_empty(self, mock_write):
        self.assertFalse(self.connection.writeQueue)
        await self.connection.drain()
        self.assertIs(mock_write.called, False)
        self.assertFalse(self.connection.writeQueue)

    @patch.object(connection.ConnectionHandler, 'write')
    async def test_drain(self, mock_write):
        message = IrcMessage(None, None, 1)
        self.connection.queue_write(message)
        await self.connection.drain()
        mock_write.assert_called_once_with(message)
        self.assertFalse(self.connection.writeQueue)

    @patch.object(connection.ConnectionHandler, 'write')
    async def test_drain_channel(self, mock_write):
        message = IrcMessage(None, None, 1)
        self.connection.queue_write(message, channel=self.channel)
        await self.connection.drain()
        mock_write.assert_called_once_with(message, channel=self.channel)
        self.assertIs(mock_write.called, True)
        self.assertFalse(self.connection.writeQueue)

    @patch.object(connection.ConnectionHandler, 'write')
    async def test_drain_whisper(self, mock_write):
        message = IrcMessage(None, None, 1)
        self.connection.queue_write(message, whisper=self.whisper)
        await self.connection.drain()
        mock_write.assert_called_once_with(message, whisper=self.whisper)
        self.assertIs(mock_write.called, True)
        self.assertFalse(self.connection.writeQueue)

    @patch('bot.utils.logException', autospec=True)
    @patch.object(connection.ConnectionHandler, '_on_write', autospec=True)
    @patch.object(connection.ConnectionHandler, '_log_write', autospec=True)
    async def test_write(self, mock_log_write, mock_on_write,
                         mock_logException):
        message = IrcMessage(None, None, 1)
        await self.connection.write(message)
        mock_log_write.assert_called_once_with(
            self.connection, message, channel=None, whisper=None,
            timestamp=self.now)
        self.mock_writer.write.assert_any_call(b'001')
        self.mock_writer.write.assert_any_call(b'\r\n')
        self.mock_writer.drain.assert_called_with()
        mock_on_write.assert_called_once_with(
            self.connection, message, self.now, channel=None)
        self.assertFalse(mock_logException.called)
        self.assertFalse(mock_logException.called)

    @patch('bot.utils.logException', autospec=True)
    @patch.object(connection.ConnectionHandler, '_log_write', autospec=True)
    async def test_write_channel_whisper(self, mock_log_write,
                                         mock_logException):
        message = IrcMessage(None, None, 1)
        await self.connection.write(message, channel=self.channel,
                                    whisper=self.whisper)
        mock_log_write.assert_called_once_with(
            self.connection, message, channel=self.channel,
            whisper=self.whisper, timestamp=self.now)
        self.mock_writer.write.assert_any_call(b'001')
        self.mock_writer.write.assert_any_call(b'\r\n')
        self.mock_writer.drain.assert_called_once_with()
        self.assertFalse(mock_logException.called)

    @patch('bot.utils.logException', autospec=True)
    @patch.object(connection.ConnectionHandler, '_log_write', autospec=True)
    async def test_write_ConnectionError(self, mock_log_write,
                                         mock_logException):
        self.mock_writer.drain.side_effect = ConnectionError
        message = IrcMessage(None, None, 1)
        with self.assertRaises(ConnectionError):
            await self.connection.write(message)
        self.assertFalse(mock_log_write.called)
        self.mock_writer.write.assert_any_call(b'001')
        self.mock_writer.write.assert_any_call(b'\r\n')
        self.mock_writer.drain.assert_called_once_with()
        mock_logException.assert_called_once_with()

    @patch('bot.globals', autospec=True)
    @patch('bot.utils.logException', autospec=True)
    @patch.object(connection.ConnectionHandler, '_log_read', autospec=True)
    @patch('source.ircmessage.parseMessage', autospec=True)
    async def test_read(self, mock_parseMessage,  mock_log_read,
                        mock_logException, mock_globals):
        mock_globals.running = True
        self.mock_reader.readuntil.return_value = b'001\r\n'
        await self.connection.read()
        self.mock_reader.readuntil.assert_called_once_with(b'\r\n')
        mock_parseMessage.assert_called_once_with(
            self.connection, '001', self.now)
        self.assertTrue(mock_log_read.called)
        self.assertFalse(mock_logException.called)
        self.assertTrue(mock_globals.running)

    @patch('bot.globals', autospec=True)
    @patch('bot.utils.logException', autospec=True)
    @patch.object(connection.ConnectionHandler, '_log_read', autospec=True)
    @patch('source.ircmessage.parseMessage', autospec=True)
    async def test_read_ConnectionError(self, mock_parseMessage, mock_log_read,
                                        mock_logException, mock_globals):
        mock_globals.running = True
        self.mock_reader.readuntil.side_effect = ConnectionError
        await self.connection.read()
        self.assertFalse(mock_log_read.called)
        self.assertFalse(mock_parseMessage.called)
        mock_logException.assert_called_once_with()
        self.assertTrue(mock_globals.running)

    @patch('bot.globals', autospec=True)
    @patch('bot.utils.logException', autospec=True)
    @patch.object(connection.ConnectionHandler, '_log_read', autospec=True)
    @patch('source.ircmessage.parseMessage', autospec=True)
    async def test_read_ConnectionReset(self, mock_parseMessage, mock_log_read,
                                        mock_logException, mock_globals):
        mock_globals.running = True
        self.mock_reader.readuntil.return_value = b'001\r\n'
        mock_parseMessage.side_effect = ConnectionReset
        with self.assertRaises(ConnectionReset):
            await self.connection.read()
        self.assertTrue(mock_log_read.called)
        self.assertTrue(mock_parseMessage.called)
        self.assertFalse(mock_logException.called)
        self.assertTrue(mock_globals.running)

    @patch('bot.globals', autospec=True)
    @patch('bot.utils.logException', autospec=True)
    @patch.object(connection.ConnectionHandler, '_log_read', autospec=True)
    @patch('source.ircmessage.parseMessage', autospec=True)
    async def test_read_LoginUnsuccessful(
            self, mock_parseMessage, mock_log_read,
            mock_logException, mock_globals):
        mock_globals.running = True
        self.mock_reader.readuntil.return_value = b'001\r\n'
        mock_parseMessage.side_effect = LoginUnsuccessful
        with self.assertRaises(LoginUnsuccessful):
            await self.connection.read()
        self.assertTrue(mock_log_read.called)
        self.assertTrue(mock_parseMessage.called)
        self.assertFalse(mock_logException.called)
        self.assertFalse(mock_globals.running)
