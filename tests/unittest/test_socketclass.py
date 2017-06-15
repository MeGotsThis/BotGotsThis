import unittest
from bot.data import Channel, ChatMessage, Socket, MessagingQueue
from bot.data import WhisperMessage
from bot.data.error import ConnectionReset, LoginUnsuccessful
from bot.thread.join import JoinThread
from bot.twitchmessage import IrcMessage
from datetime import datetime, timedelta
from io import StringIO
from unittest.mock import Mock, patch


class SocketSpec():
    @staticmethod
    def connect(address):
        pass

    @staticmethod
    def recv(bufsize, flags=0):
        pass

    @staticmethod
    def send(bytes, flags=0):
        pass

    @staticmethod
    def close():
        pass


class TestSocket(unittest.TestCase):
    def setUp(self):
        self.socket = Socket('Kappa', 'irc.twitch.tv', 6667)
        self.channel = Channel('botgotsthis', self.socket)
        self.whisper = WhisperMessage('botgotsthis', 'Kappa')

    def test_name(self):
        self.assertEqual(self.socket.name, 'Kappa')

    def test_server(self):
        self.assertEqual(self.socket.server, 'irc.twitch.tv')

    def test_port(self):
        self.assertEqual(self.socket.port, 6667)

    def test_address(self):
        self.assertEqual(self.socket.address, ('irc.twitch.tv', 6667))

    def test_socket(self):
        self.assertEqual(self.socket.socket, None)

    def test_isConnected(self):
        self.assertIs(self.socket.isConnected, False)

    def test_channels(self):
        self.assertEqual(self.socket.channels, {})

    def test_messaging(self):
        self.assertIsInstance(self.socket.messaging, MessagingQueue)

    def test_writeQueue(self):
        self.assertFalse(self.socket.writeQueue, MessagingQueue)

    def test_fileno(self):
        self.assertFalse(self.socket.fileno(), None)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.coroutine.join.connected', autospec=True)
    @patch('bot.data.socket.socket.connect', spec=SocketSpec.connect)
    @patch.object(Socket, 'login', autospec=True)
    def test_connect(self, mock_login, mock_connect, mock_connected, mock_now,
                     mock_stdout):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        self.socket.connect()
        mock_connect.assert_any_call(('irc.twitch.tv', 6667))
        mock_connected.assert_called_with(self.socket)
        self.assertNotEquals(mock_stdout.getvalue(), '')
        mock_login.assert_called_once_with(self.socket, self.socket.socket)
        self.assertEqual(self.socket.lastSentPing, now)
        self.assertEqual(self.socket.lastPing, now)
        self.assertEqual(self.socket.lastConnectAttempt, now)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.utils.now', autospec=True)
    @patch('bot.coroutine.join.connected', autospec=True)
    @patch('bot.data.socket.socket.connect', spec=SocketSpec.connect)
    @patch.object(Socket, 'login', autospec=True)
    def test_connect_throttle(self, mock_login, mock_connect, mock_connected,
                              mock_now, mock_stdout):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        self.socket.lastConnectAttempt = now
        self.socket.connect()
        mock_connect.assert_not_called()
        mock_connected.assert_not_called()
        self.assertEquals(mock_stdout.getvalue(), '')
        self.assertFalse(mock_login.called)
        self.assertEqual(self.socket.lastSentPing, datetime.max)
        self.assertEqual(self.socket.lastPing, datetime.max)
        self.assertEqual(self.socket.lastConnectAttempt, now)

    def test_login_none(self):
        self.assertRaises(TypeError, self.socket.login, None)

    @patch('socket.socket', spec=True)
    @patch('bot.config', autospec=True)
    @patch.object(Socket, '_logWrite', autospec=True)
    def test_login(self, mock_logWrite, mock_config, MockSocket):
        socket = MockSocket()
        mock_config.botnick = 'botgotsthis'
        mock_config.password = 'oauth:some_long_oauth_token_here'
        self.socket.login(socket)
        self.assertGreaterEqual(socket.send.call_count, 3)
        self.assertEqual(socket.send.call_count, mock_logWrite.call_count)

    def test_disconnect(self):
        self.assertRaises(ConnectionError, self.socket.disconnect)

    def test_write_none(self):
        self.assertRaises(TypeError, self.socket.write, None)

    def test_write(self):
        self.assertRaises(ConnectionError, self.socket.write,
                          IrcMessage(None, None, 'PING'))

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.coroutine.join.record_join', autospec=True)
    @patch.object(Channel, 'onJoin', autospec=True)
    def test_onwrite_join(self, mock_onJoin, mock_record_join, mock_stdout):
        now = datetime(2000, 1, 1)
        message = IrcMessage(None, None, 'JOIN')
        self.socket._onWrite(message, now, channel=self.channel)
        mock_onJoin.assert_called_once_with(self.channel)
        mock_record_join.assert_called_once_with()
        self.assertNotEquals(mock_stdout.getvalue(), '')

    def test_onwrite_ping(self):
        now = datetime(2000, 1, 1)
        message = IrcMessage(None, None, 'PING')
        self.socket._onWrite(message, now, channel=self.channel)
        self.assertEqual(self.socket.lastSentPing, now)

    @patch.object(Socket, 'write', autospec=True)
    def test_flushWrite(self, mock_write):
        self.assertRaises(ConnectionError, self.socket.flushWrite)

    def test_read(self):
        self.assertRaises(ConnectionError, self.socket.read)

    @patch.object(Socket, 'queueWrite', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_ping(self, mock_now, mock_queueWrite):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        self.socket.ping()
        self.assertIs(mock_queueWrite.called, True)
        self.assertTrue(any(m for m in mock_queueWrite.call_args_list
                            if m[0][1].command == 'PONG'))
        self.assertEqual(self.socket.lastPing, now)

    @patch.object(Socket, 'disconnect', autospec=True)
    @patch.object(Socket, 'queueWrite', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_sendPing_tooSoon(self, mock_now, mock_queueWrite, mock_disconnect):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        self.socket.lastSentPing = now
        self.socket.lastPing = now
        self.socket.sendPing()
        self.assertFalse(mock_disconnect.called)
        self.assertFalse(mock_queueWrite.called)

    @patch.object(Socket, 'disconnect', autospec=True)
    @patch.object(Socket, 'queueWrite', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_sendPing(self, mock_now, mock_config, mock_queueWrite,
                      mock_disconnect):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_config.botnick = 'botgotsthis'
        self.socket.lastSentPing = now - timedelta(minutes=1, seconds=1)
        self.socket.lastPing = now
        self.socket.sendPing()
        self.assertFalse(mock_disconnect.called)
        self.assertIs(mock_queueWrite.called, True)
        self.assertTrue(any(m for m in mock_queueWrite.call_args_list
                            if m[0][1].command == 'PING'))

    @patch.object(Socket, 'disconnect', autospec=True)
    @patch.object(Socket, 'queueWrite', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_sendPing_noresponse(self, mock_now, mock_config, mock_queueWrite,
                              mock_disconnect):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_config.botnick = 'botgotsthis'
        self.socket.lastSentPing = now
        self.socket.lastPing = now - timedelta(minutes=2)
        self.socket.sendPing()
        self.assertTrue(mock_disconnect.called)
        self.assertFalse(mock_queueWrite.called)

    @patch.object(Socket, 'disconnect', autospec=True)
    @patch.object(Socket, 'queueWrite', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_sendPing_noresponse_late(self, mock_now, mock_config,
                                      mock_queueWrite, mock_disconnect):
        now = datetime(2000, 1, 1)
        mock_now.return_value = now
        mock_config.botnick = 'botgotsthis'
        self.socket.lastSentPing = now - timedelta(minutes=1, seconds=1)
        self.socket.lastPing = now - timedelta(minutes=2)
        self.socket.sendPing()
        self.assertFalse(mock_disconnect.called)
        self.assertIs(mock_queueWrite.called, True)
        self.assertTrue(any(m for m in mock_queueWrite.call_args_list
                            if m[0][1].command == 'PING'))

    @patch('bot.config', autospec=True)
    @patch('bot.utils.logIrcMessage', autospec=True)
    def test_logRead(self, mock_logIrcMessage, mock_config):
        mock_config.botnick = 'botgotsthis'
        self.socket._logRead('')
        self.assertTrue(mock_logIrcMessage.called)

    @patch('bot.config', autospec=True)
    @patch('bot.utils.logIrcMessage', autospec=True)
    def test_logWrite(self, mock_logIrcMessage, mock_config):
        mock_config.botnick = 'botgotsthis'
        self.socket._logWrite(IrcMessage(None, None, 1))
        self.assertTrue(mock_logIrcMessage.called)

    @patch('bot.config', autospec=True)
    @patch('bot.utils.logIrcMessage', autospec=True)
    def test_logWrite_channel(self, mock_logIrcMessage, mock_config):
        mock_config.botnick = 'botgotsthis'
        self.socket._logWrite(IrcMessage(None, None, 1), channel=self.channel)
        self.assertEqual(mock_logIrcMessage.call_count, 2)

    @patch('bot.config', autospec=True)
    @patch('bot.utils.logIrcMessage', autospec=True)
    def test_logWrite_whisper(self, mock_logIrcMessage, mock_config):
        mock_config.botnick = 'botgotsthis'
        self.socket._logWrite(IrcMessage(None, None, 1), whisper=self.whisper)
        self.assertEqual(mock_logIrcMessage.call_count, 4)

    @patch('bot.config', autospec=True)
    @patch('bot.utils.logIrcMessage', autospec=True)
    def test_logWrite_channel_whisper(self, mock_logIrcMessage, mock_config):
        mock_config.botnick = 'botgotsthis'
        self.assertRaises(ValueError, self.socket._logWrite,
                          IrcMessage(None, None, 1),
                          channel=self.channel, whisper=self.whisper)
        self.assertEqual(mock_logIrcMessage.call_count, 1)

    def test_queueWrite_none(self):
        self.assertRaises(TypeError, self.socket.queueWrite, None)

    def test_queueWrite_channel_int(self):
        self.assertRaises(TypeError, self.socket.queueWrite,
                          IrcMessage(None, None, 1), channel=1)

    def test_queueWrite_whisper_int(self):
        self.assertRaises(TypeError, self.socket.queueWrite,
                          IrcMessage(None, None, 1), whisper=1)

    def test_queueWrite_channel_whisper(self):
        self.assertRaises(ValueError, self.socket.queueWrite,
                          IrcMessage(None, None, 1),
                          channel=self.channel,
                          whisper=self.whisper)

    def test_queueWrite(self):
        message = IrcMessage(None, None, 1)
        self.socket.queueWrite(message)
        self.assertEqual(len(self.socket.writeQueue), 1)
        self.assertEqual(self.socket.writeQueue[0][0], (message,))
        self.assertEqual(self.socket.writeQueue[0][1], {})

    def test_queueWrite_channel(self):
        message = IrcMessage(None, None, 1)
        self.socket.queueWrite(message, channel=self.channel)
        self.assertEqual(len(self.socket.writeQueue), 1)
        self.assertEqual(self.socket.writeQueue[0][0], (message,))
        self.assertEqual(self.socket.writeQueue[0][1],
                         {'channel': self.channel})

    def test_queueWrite_whisper(self):
        message = IrcMessage(None, None, 1)
        self.socket.queueWrite(message, whisper=self.whisper)
        self.assertEqual(len(self.socket.writeQueue), 1)
        self.assertEqual(self.socket.writeQueue[0][0], (message,))
        self.assertEqual(self.socket.writeQueue[0][1],
                         {'whisper': self.whisper})

    def test_queueWrite_multi(self):
        message1 = IrcMessage(None, None, 1)
        message2 = IrcMessage(None, None, 2)
        self.socket.queueWrite(message1)
        self.socket.queueWrite(message2)
        self.assertEqual(len(self.socket.writeQueue), 2)
        self.assertEqual(self.socket.writeQueue[0][0], (message1,))
        self.assertEqual(self.socket.writeQueue[1][0], (message2,))

    def test_queueWrite_multi_prepend(self):
        message1 = IrcMessage(None, None, 1)
        message2 = IrcMessage(None, None, 2)
        self.socket.queueWrite(message1)
        self.socket.queueWrite(message2, prepend=True)
        self.assertEqual(len(self.socket.writeQueue), 2)
        self.assertEqual(self.socket.writeQueue[0][0], (message2,))
        self.assertEqual(self.socket.writeQueue[1][0], (message1,))

    def test_joinChannel(self):
        self.socket.joinChannel(self.channel)
        self.assertIn(self.channel.channel, self.socket._channels)
        self.assertIs(self.socket._channels[self.channel.channel],
                      self.channel)

    @patch('bot.globals', autospec=True)
    @patch.object(Socket, 'queueWrite', autospec=True)
    def test_partChannel(self, mock_queueWrite, mock_globals):
        self.socket.partChannel(self.channel)
        self.assertNotIn(self.channel.channel, self.socket._channels)
        self.assertFalse(mock_queueWrite.called)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.coroutine.join.on_part', autospec=True)
    @patch.object(Socket, 'queueWrite', autospec=True)
    def test_partChannel_contains(self, mock_queueWrite, mock_on_part,
                                  mock_stdout):
        self.socket._channels[self.channel.channel] = self.channel
        self.socket.partChannel(self.channel)
        self.assertNotIn(self.channel.channel, self.socket._channels)
        self.assertTrue(mock_queueWrite.called)
        self.assertTrue(mock_on_part.called)
        self.assertTrue(any(m for m in mock_queueWrite.call_args_list
                            if m[0][1].command == 'PART'))
        self.assertNotEquals(mock_stdout.getvalue(), '')

    @patch('bot.globals', autospec=True)
    @patch.object(MessagingQueue, 'popChat', autospec=True)
    @patch.object(MessagingQueue, 'popWhisper', autospec=True)
    @patch.object(Socket, 'queueWrite', autospec=True)
    def test_queueMessages(self, mock_queueWrite, mock_popWhisper,
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
        self.socket.queueMessages()
        self.assertEqual(mock_queueWrite.call_count, 4)
        self.assertTrue(len([m for m in mock_queueWrite.call_args_list
                             if m[0][1].command == 'PRIVMSG']), 4)
        self.assertTrue(len([m for m in mock_queueWrite.call_args_list
                             if 'channel' in m[1]
                             and m[1]['channel'] is self.channel]), 2)
        self.assertTrue(len([m for m in mock_queueWrite.call_args_list
                             if 'whisper' in m[1]
                             and m[1]['whisper'].nick in ['megotsthis',
                                                          'botgotsthis']]), 2)


class TestSocketConnected(unittest.TestCase):
    def setUp(self):
        self.socket = Socket('Kappa', 'irc.twitch.tv', 6667)
        self.channel = Channel('botgotsthis', self.socket)
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

        patcher = patch('bot.coroutine.join.disconnected', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_disconnected = patcher.start()

        patch_connect = patch('socket.socket.connect',
                              spec=SocketSpec.connect)
        patch_connect.start()
        patch_stdout = patch('sys.stdout', new_callable=StringIO)
        patch_stdout.start()
        patch_login = patch.object(Socket, 'login', autospec=True)
        patch_login.start()

        self.socket.connect()

        patch_connect.stop()
        patch_stdout.stop()
        patch_login.stop()

    def test_fileno(self):
        self.assertEqual(self.socket.fileno(), self.socket.socket.fileno())

    def test_connect(self):
        self.assertRaises(ConnectionError, self.socket.connect)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('bot.data.socket.socket.close', spec=SocketSpec.close)
    def test_disconnect(self, mock_close, mock_stdout):
        self.socket.disconnect()
        self.assertIsNone(self.socket.socket)
        self.assertTrue(mock_close.called)
        self.assertTrue(self.mock_disconnected.called)
        self.assertEqual(self.socket.lastPing, datetime.max)
        self.assertEqual(self.socket.lastSentPing, datetime.max)

    @patch.object(Socket, 'write', autospec=True)
    def test_flushWrite_empty(self, mock_write):
        self.assertFalse(self.socket.writeQueue)
        self.socket.flushWrite()
        self.assertIs(mock_write.called, False)
        self.assertFalse(self.socket.writeQueue)

    @patch.object(Socket, 'write', autospec=True)
    def test_flushWrite(self, mock_write):
        message = IrcMessage(None, None, 1)
        self.socket.queueWrite(message)
        self.socket.flushWrite()
        mock_write.assert_called_once_with(self.socket, message)
        self.assertIs(mock_write.called, True)
        self.assertFalse(self.socket.writeQueue)

    @patch.object(Socket, 'write', autospec=True)
    def test_flushWrite_channel(self, mock_write):
        message = IrcMessage(None, None, 1)
        self.socket.queueWrite(message, channel=self.channel)
        self.socket.flushWrite()
        mock_write.assert_called_once_with(self.socket, message,
                                           channel=self.channel)
        self.assertIs(mock_write.called, True)
        self.assertFalse(self.socket.writeQueue)

    @patch.object(Socket, 'write', autospec=True)
    def test_flushWrite_whisper(self, mock_write):
        message = IrcMessage(None, None, 1)
        self.socket.queueWrite(message, whisper=self.whisper)
        self.socket.flushWrite()
        mock_write.assert_called_once_with(self.socket, message,
                                           whisper=self.whisper)
        self.assertIs(mock_write.called, True)
        self.assertFalse(self.socket.writeQueue)

    @patch.object(Socket, 'disconnect', autospec=True)
    @patch('bot.utils.logException', autospec=True)
    @patch('bot.data.socket.socket.send', spec=SocketSpec.send)
    @patch.object(Socket, '_onWrite', autospec=True)
    @patch.object(Socket, '_logWrite', autospec=True)
    def test_write(self, mock_logWrite, mock_onWrite, mock_send, mock_logException,
                   mock_disconnect):
        message = IrcMessage(None, None, 1)
        self.socket.write(message)
        mock_logWrite.assert_called_once_with(self.socket, message,
                                              channel=None, whisper=None,
                                              timestamp=self.now)
        mock_send.assert_called_once_with(b'001\r\n')
        mock_onWrite.assert_called_once_with(self.socket, message, self.now, channel=None)
        self.assertFalse(mock_logException.called)
        self.assertFalse(mock_logException.called)
        self.assertFalse(mock_disconnect.called)

    @patch.object(Socket, 'disconnect', autospec=True)
    @patch('bot.utils.logException', autospec=True)
    @patch('bot.data.socket.socket.send', spec=SocketSpec.send)
    @patch.object(Socket, '_logWrite', autospec=True)
    def test_write_channel_whisper(self, mock_logWrite, mock_send,
                                   mock_logException, mock_disconnect):
        message = IrcMessage(None, None, 1)
        self.socket.write(message, channel=self.channel, whisper=self.whisper)
        mock_logWrite.assert_called_once_with(self.socket, message,
                                              channel=self.channel,
                                              whisper=self.whisper,
                                              timestamp=self.now)
        mock_send.assert_called_once_with(b'001\r\n')
        self.assertFalse(mock_logException.called)
        self.assertFalse(mock_disconnect.called)

    @patch.object(Socket, 'disconnect', autospec=True)
    @patch('bot.utils.logException', autospec=True)
    @patch('bot.data.socket.socket.send', spec=SocketSpec.send)
    @patch.object(Socket, '_logWrite', autospec=True)
    def test_write_ConnectionError(self, mock_logWrite, mock_send,
                                   mock_logException, mock_disconnect):
        mock_send.side_effect = ConnectionError
        message = IrcMessage(None, None, 1)
        self.socket.write(message)
        self.assertFalse(mock_logWrite.called)
        mock_send.assert_called_once_with(b'001\r\n')
        mock_logException.assert_called_once_with()
        mock_disconnect.assert_called_once_with(self.socket)

    @patch('bot.globals', autospec=True)
    @patch.object(Socket, 'disconnect', autospec=True)
    @patch('bot.utils.logException', autospec=True)
    @patch.object(Socket, '_logRead', autospec=True)
    @patch('source.ircmessage.parseMessage', autospec=True)
    @patch('bot.data.socket.socket.recv', spec=SocketSpec.recv)
    def test_read(self, mock_recv, mock_parseMessage, mock_logRead,
                  mock_logException, mock_disconnect, mock_globals):
        mock_globals.running = True
        mock_recv.side_effect = [b'001\r\n']
        self.socket.read()
        mock_logRead.assert_called_once_with(self.socket, '001')
        mock_parseMessage.assert_called_once_with(self.socket, '001', self.now)
        self.assertFalse(mock_logException.called)
        self.assertFalse(mock_disconnect.called)
        self.assertTrue(mock_globals.running)

    @patch('bot.globals', autospec=True)
    @patch.object(Socket, 'disconnect', autospec=True)
    @patch('bot.utils.logException', autospec=True)
    @patch.object(Socket, '_logRead', autospec=True)
    @patch('source.ircmessage.parseMessage', autospec=True)
    @patch('bot.data.socket.socket.recv', spec=SocketSpec.recv)
    def test_read_ConnectionError(
            self, mock_recv, mock_parseMessage, mock_logRead,
            mock_logException, mock_disconnect, mock_globals):
        mock_globals.running = True
        mock_recv.side_effect = ConnectionError
        self.socket.read()
        self.assertFalse(mock_logRead.called)
        self.assertFalse(mock_parseMessage.called)
        mock_logException.assert_called_once_with()
        mock_disconnect.assert_called_once_with(self.socket)
        self.assertTrue(mock_globals.running)

    @patch('bot.globals', autospec=True)
    @patch.object(Socket, 'disconnect', autospec=True)
    @patch('bot.utils.logException', autospec=True)
    @patch.object(Socket, '_logRead', autospec=True)
    @patch('source.ircmessage.parseMessage', autospec=True)
    @patch('bot.data.socket.socket.recv', spec=SocketSpec.recv)
    def test_read_ConnectionReset(
            self, mock_recv, mock_parseMessage, mock_logRead,
            mock_logException, mock_disconnect, mock_globals):
        mock_globals.running = True
        mock_recv.side_effect = [b'001\r\n']
        mock_parseMessage.side_effect = ConnectionReset
        self.socket.read()
        self.assertTrue(mock_logRead.called)
        self.assertTrue(mock_parseMessage.called)
        self.assertFalse(mock_logException.called)
        mock_disconnect.assert_called_once_with(self.socket)
        self.assertTrue(mock_globals.running)

    @patch('bot.globals', autospec=True)
    @patch.object(Socket, 'disconnect', autospec=True)
    @patch('bot.utils.logException', autospec=True)
    @patch.object(Socket, '_logRead', autospec=True)
    @patch('source.ircmessage.parseMessage', autospec=True)
    @patch('bot.data.socket.socket.recv', spec=SocketSpec.recv)
    def test_read_LoginUnsuccessful(
            self, mock_recv, mock_parseMessage, mock_logRead,
            mock_logException, mock_disconnect, mock_globals):
        mock_globals.running = True
        mock_recv.side_effect = [b'001\r\n']
        mock_parseMessage.side_effect = LoginUnsuccessful
        self.socket.read()
        self.assertTrue(mock_logRead.called)
        self.assertTrue(mock_parseMessage.called)
        self.assertFalse(mock_logException.called)
        mock_disconnect.assert_called_once_with(self.socket)
        self.assertFalse(mock_globals.running)
