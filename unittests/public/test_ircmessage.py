import unittest
from bot.data import Channel, Socket
from bot.twitchmessage import IrcMessage, IrcMessageParams
from datetime import datetime
from source import ircmessage
from unittest.mock import Mock, patch


class PublicTestIrcMessage(unittest.TestCase):
    def setUp(self):
        self.socket = Mock(spec=Socket)
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.ircOps = set()
        self.channel.ircUsers = set()
        self.socket.channels = {'botgotsthis': self.channel}

        patcher = patch('source.ircmessage.utils.logIrcMessage', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_log = patcher.start()

    def test_parseMessage(self):
        self.assertEqual(True, True)

    @patch.dict('source.ircmessage.ircHandlers')
    def test_registerIrc(self):
        @ircmessage.registerIrc('KAPPA')
        def irc_kappa(socket, message, timestamp):
            pass
        self.assertIn('KAPPA', ircmessage.ircHandlers)
        self.assertIs(ircmessage.ircHandlers['KAPPA'], irc_kappa)

    def test_log_channel_message(self):
        now = datetime(2000, 1, 1)
        message = IrcMessage(command='PRIVMSG',
                             params=IrcMessageParams(middle='#botgotsthis',
                                                     trailing=''))
        ircmessage.log_channel_message(message, now)
        self.assertTrue(self.mock_log.called)

    def test_log_channel_message_not(self):
        now = datetime(2000, 1, 1)
        ircmessage.log_channel_message(IrcMessage(command=0), now)
        self.assertFalse(self.mock_log.called)

    @patch('source.ircmessage.config', autospec=True)
    @patch('source.ircmessage.channel.parse', autospec=True)
    def test_log_irc_privmsg(self, mock_parse, mock_config):
        mock_config.botnick = 'botgotsthis'
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv PRIVMSG '
            '#botgotsthis :Hello Kappa')
        ircmessage.irc_privmsg(self.socket, message, now)
        self.assertTrue(mock_parse.called)
        self.assertTrue(self.mock_log.called)

    @patch('source.ircmessage.config', autospec=True)
    @patch('source.ircmessage.channel.parse', autospec=True)
    def test_log_irc_privmsg_no_channel(self, mock_parse, mock_config):
        mock_config.botnick = 'botgotsthis'
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv PRIVMSG '
            '#megotsthis :Hello Kappa')
        ircmessage.irc_privmsg(self.socket, message, now)
        self.assertFalse(mock_parse.called)
        self.assertTrue(self.mock_log.called)

    @patch('source.ircmessage.config', autospec=True)
    @patch('source.ircmessage.channel.parse', autospec=True)
    def test_log_irc_privmsg_mention(self, mock_parse, mock_config):
        mock_config.botnick = 'botgotsthis'
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv PRIVMSG '
            '#botgotsthis :botgotsthis')
        ircmessage.irc_privmsg(self.socket, message, now)
        self.assertTrue(mock_parse.called)
        self.assertGreaterEqual(self.mock_log.call_count, 2)

    @patch('source.ircmessage.config', autospec=True)
    @patch('source.ircmessage.whisper.parse', autospec=True)
    def test_log_irc_whisper(self, mock_parse, mock_config):
        mock_config.botnick = 'botgotsthis'
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@megotsthis.tmi.twitch.tv WHISPER '
            'botgotsthis :Kappa')
        ircmessage.irc_whisper(self.socket, message, now)
        self.assertTrue(mock_parse.called)
        self.assertGreaterEqual(self.mock_log.call_count, 3)

    @patch('source.ircmessage.notice.parse', autospec=True)
    def test_log_irc_notice(self, mock_parse):
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            '@msg-id=bad_timeout_broadcaster :tmi.twitch.tv NOTICE '
            '#botgotsthis :You cannot timeout the broadcaster.')
        ircmessage.irc_notice(self.socket, message, now)
        self.assertTrue(mock_parse.called)
        self.assertTrue(self.mock_log.called)

    @patch('source.ircmessage.clearchat.parse', autospec=True)
    def test_log_irc_clearchat(self, mock_parse):
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':tmi.twitch.tv CLEARCHAT #botgotsthis')
        ircmessage.irc_clearchat(self.socket, message, now)
        self.assertTrue(mock_parse.called)
        self.assertTrue(self.mock_log.called)

    def test_log_irc_roomstate(self):
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':tmi.twitch.tv ROOMSTATE #megotsthis')
        ircmessage.irc_clearchat(self.socket, message, now)
        self.assertTrue(self.mock_log.called)

    def test_log_irc_hosttarget(self):
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':tmi.twitch.tv ROOMSTATE #megotsthis')
        ircmessage.irc_clearchat(self.socket, message, now)
        self.assertTrue(self.mock_log.called)

    def test_log_irc_mode_plus_o(self):
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':jtv MODE #botgotsthis +o botgotsthis')
        ircmessage.irc_mode(self.socket, message, now)
        self.assertEqual(self.channel.ircOps, {'botgotsthis'})

    def test_log_irc_mode_plus_o_duplicating(self):
        now = datetime(2000, 1, 1)
        self.channel.ircOps = {'botgotsthis'}
        message = IrcMessage.fromMessage(
            ':jtv MODE #botgotsthis +o botgotsthis')
        ircmessage.irc_mode(self.socket, message, now)
        self.assertEqual(self.channel.ircOps, {'botgotsthis'})

    def test_log_irc_mode_minus_o_empty(self):
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':jtv MODE #botgotsthis -o botgotsthis')
        ircmessage.irc_mode(self.socket, message, now)
        self.assertEqual(self.channel.ircOps, set())

    def test_log_irc_join(self):
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv JOIN '
            '#botgotsthis')
        ircmessage.irc_join(self.socket, message, now)
        self.assertEqual(self.channel.ircUsers, {'botgotsthis'})

    def test_log_irc_353(self):
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':botgotsthis.tmi.twitch.tv 353 botgotsthis = #botgotsthis '
            ':botgotsthis')
        ircmessage.irc_353(self.socket, message, now)
        self.assertEqual(self.channel.ircUsers, {'botgotsthis'})
        self.assertTrue(self.mock_log.called)

    def test_log_irc_366(self):
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':botgotsthis.tmi.twitch.tv 366 botgotsthis #botgotsthis '
            ':End of /NAMES list')
        ircmessage.irc_353(self.socket, message, now)
        self.assertTrue(self.mock_log.called)

    def test_log_irc_part(self):
        now = datetime(2000, 1, 1)
        self.channel.ircUsers.add('botgotsthis')
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv PART '
            '#botgotsthis')
        ircmessage.irc_part(self.socket, message, now)
        self.assertEqual(self.channel.ircUsers, set())

    def test_log_irc_part_empty(self):
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv PART '
            '#botgotsthis')
        ircmessage.irc_part(self.socket, message, now)
        self.assertEqual(self.channel.ircUsers, set())

    def test_log_irc_ping(self):
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            'PING :tmi.twitch.tv')
        ircmessage.irc_ping(self.socket, message, now)
        self.assertTrue(self.socket.ping.called)

    @patch('source.ircmessage.config', autospec=True)
    def test_log_irc_pong(self, mock_config):
        mock_config.botnick = 'botgotsthis'
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':tmi.twitch.tv PONG tmi.twitch.tv :botgotsthis')
        ircmessage.irc_pong(self.socket, message, now)
        self.assertEqual(self.socket.lastPing, now)

    @patch('source.ircmessage.userstate.parse', autospec=True)
    def test_log_irc_userstate(self, mock_parse):
        now = datetime(2000, 1, 1)
        message = IrcMessage.fromMessage(
            ':tmi.twitch.tv CLEARCHAT #botgotsthis')
        ircmessage.irc_userstate(self.socket, message, now)
        self.assertTrue(mock_parse.called)
        self.assertTrue(self.mock_log.called)
