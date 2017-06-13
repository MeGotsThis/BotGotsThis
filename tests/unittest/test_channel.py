import asynctest
import math
import unittest
from bot.data import Channel, MessagingQueue, Socket
from collections.abc import MutableMapping, MutableSet
from datetime import datetime
from asynctest.mock import Mock, patch


class TestChannel(unittest.TestCase):
    def setUp(self):
        self.socket = Mock(spec=Socket)
        self.socket.messaging = Mock(spec=MessagingQueue)
        self.channel = Channel('botgotsthis', self.socket)

    def test_constructor_name_none(self):
        self.assertRaises(TypeError, Channel, None, self.socket)

    def test_constructor_name_bytes(self):
        self.assertRaises(TypeError, Channel, b'', self.socket)

    def test_constructor_socket_none(self):
        self.assertRaises(TypeError, Channel, 'botgotsthis', None)

    def test_constructor_name_empty(self):
        self.assertRaises(ValueError, Channel, '', self.socket)

    def test_channel(self):
        self.assertEqual(self.channel.channel, 'botgotsthis')

    def test_ircChannel(self):
        self.assertEqual(self.channel.ircChannel, '#botgotsthis')

    def test_socket(self):
        self.assertIs(self.channel.socket, self.socket)

    def test_isMod(self):
        self.assertIs(self.channel.isMod, False)

    def test_isMod_true(self):
        self.channel.isMod = True
        self.assertIs(self.channel.isMod, True)

    def test_isMod_int(self):
        self.channel.isMod = 1
        self.assertIs(self.channel.isMod, True)

    def test_isSubscriber(self):
        self.assertIs(self.channel.isSubscriber, False)

    def test_isSubscriber_true(self):
        self.channel.isSubscriber = True
        self.assertIs(self.channel.isSubscriber, True)

    def test_isSubscriber_int(self):
        self.channel.isSubscriber = 1
        self.assertIs(self.channel.isSubscriber, True)

    def test_ircUsers(self):
        self.assertIsInstance(self.channel.ircUsers, MutableSet)
        self.assertFalse(self.channel.ircUsers)
        self.channel.ircUsers.add('botgotsthis')
        self.assertIn('botgotsthis', self.channel.ircUsers)

    def test_ircUsers_set(self):
        with self.assertRaises(AttributeError):
            self.channel.ircUsers = set()

    def test_ircOps(self):
        self.assertIsInstance(self.channel.ircOps, MutableSet)
        self.assertFalse(self.channel.ircOps)
        self.channel.ircOps.add('botgotsthis')
        self.assertIn('botgotsthis', self.channel.ircOps)

    def test_ircOps_set(self):
        with self.assertRaises(AttributeError):
            self.channel.ircOps = set()

    def test_joinPriority(self):
        self.assertEqual(self.channel.joinPriority, math.inf)

    def test_joinPriority_set(self):
        self.channel.joinPriority = 0
        self.assertEqual(self.channel.joinPriority, 0)

    def test_joinPriority_set_str(self):
        self.channel.joinPriority = '-15'
        self.assertEqual(self.channel.joinPriority, -15)

    def test_joinPriority_set_list(self):
        with self.assertRaises(TypeError):
            self.channel.joinPriority = []

    def test_sessionData(self):
        self.assertIsInstance(self.channel.sessionData, MutableMapping)
        self.assertFalse(self.channel.sessionData)
        self.channel.sessionData['Kappa'] = 'PogChamp'
        self.assertIn('Kappa', self.channel.sessionData)
        self.assertEqual(self.channel.sessionData['Kappa'], 'PogChamp')

    def test_sessionData_set(self):
        with self.assertRaises(AttributeError):
            self.channel.sessionData = {}

    def test_ffzCache(self):
        self.assertEqual(self.channel.ffzCache, datetime.min)

    def test_ffzCache_set(self):
        with self.assertRaises(AttributeError):
            self.channel.ffzCache = datetime.utcnow()

    def test_ffzEmotes(self):
        self.assertEqual(self.channel.ffzEmotes, {})

    def test_ffzEmotes_set(self):
        with self.assertRaises(AttributeError):
            self.channel.ffzEmotes = {}

    @patch('bot.utils.now', autospec=True)
    @patch('source.api.bttv.getBroadcasterEmotes', autospec=True)
    def test_updateBttvEmotes(self, mock_getBttvEmotes, mock_now):
        now = datetime(2000, 1, 1)
        emotes = {'': 'BetterTwitch.Tv'}
        mock_now.return_value = now
        mock_getBttvEmotes.return_value = emotes
        self.channel.updateBttvEmotes()
        mock_getBttvEmotes.assert_called_once_with(self.channel.channel)
        self.assertEqual(self.channel.bttvCache, now)
        self.assertEqual(self.channel.bttvEmotes, emotes)

    @patch('bot.utils.now', autospec=True)
    @patch('source.api.bttv.getBroadcasterEmotes', autospec=True)
    def test_updateBttvEmotes_empty(self, mock_getBttvEmotes, mock_now):
        now = datetime(2000, 1, 1)
        emotes = {}
        mock_now.return_value = now
        mock_getBttvEmotes.return_value = emotes
        self.channel._bttvEmotes = {'': 'BetterTwitch.Tv'}
        self.channel.updateBttvEmotes()
        mock_getBttvEmotes.assert_called_once_with(self.channel.channel)
        self.assertEqual(self.channel.bttvCache, now)
        self.assertEqual(self.channel.bttvEmotes, emotes)

    @patch('bot.utils.now', autospec=True)
    @patch('source.api.bttv.getBroadcasterEmotes', autospec=True)
    def test_updateFfzEmotes_error(self, mock_getBttvEmotes, mock_now):
        now = datetime(2000, 1, 1)
        emotes = {'': 'BetterTwitch.Tv'}
        self.channel._bttvEmotes = emotes
        mock_now.return_value = now
        mock_getBttvEmotes.return_value = None
        self.channel.updateBttvEmotes()
        self.assertEqual(self.channel.bttvCache, datetime.min)
        self.assertEqual(self.channel.bttvEmotes, emotes)

    def test_streamingSince(self):
        self.assertIsNone(self.channel.streamingSince)

    def test_streamingSince_set_none(self):
        self.channel.streamingSince = None
        self.assertIsNone(self.channel.streamingSince)

    def test_streamingSince_set_datetime(self):
        timestamp = datetime(2000, 1, 1)
        self.channel.streamingSince = timestamp
        self.assertEqual(self.channel.streamingSince, timestamp)

    def test_streamingSince_set_list(self):
        with self.assertRaises(TypeError):
            self.channel.streamingSince = []

    def test_isStreaming(self):
        self.assertIs(self.channel.isStreaming, False)

    def test_isStreaming_true(self):
        timestamp = datetime(2000, 1, 1)
        self.channel.streamingSince = timestamp
        self.assertIs(self.channel.isStreaming, True)

    def test_twitchCache(self):
        self.assertEqual(self.channel.twitchCache, datetime.min)

    def test_twitchCache_set_none(self):
        with self.assertRaises(TypeError):
            self.channel.twitchCache = None

    def test_twitchCache_set(self):
        timestamp = datetime(2000, 1, 1)
        self.channel.twitchCache = timestamp
        self.assertEqual(self.channel.twitchCache, timestamp)

    def test_twitchStatus(self):
        self.assertEqual(self.channel.twitchStatus, '')

    def test_twitchStatus_set_none(self):
        self.channel.twitchStatus = None
        self.assertIsNone(self.channel.twitchStatus)

    def test_twitchStatus_set_bytes(self):
        with self.assertRaises(TypeError):
            self.channel.twitchStatus = b''

    def test_twitchStatus_set(self):
        self.channel.twitchStatus = 'Kappa'
        self.assertEqual(self.channel.twitchStatus, 'Kappa')

    def test_twitchGame(self):
        self.assertEqual(self.channel.twitchGame, '')

    def test_twitchGame_set_none(self):
        self.channel.twitchGame = None
        self.assertIsNone(self.channel.twitchGame)

    def test_twitchGame_set_bytes(self):
        with self.assertRaises(TypeError):
            self.channel.twitchGame = b''

    def test_twitchGame_set(self):
        self.channel.twitchGame = 'Kappa'
        self.assertEqual(self.channel.twitchGame, 'Kappa')

    def test_serverCheck(self):
        self.assertEqual(self.channel.serverCheck, datetime.min)

    def test_serverCheck_set_none(self):
        with self.assertRaises(TypeError):
            self.channel.serverCheck = None

    def test_serverCheck_set(self):
        timestamp = datetime(2000, 1, 1)
        self.channel.serverCheck = timestamp
        self.assertEqual(self.channel.serverCheck, timestamp)

    def test_onJoin(self):
        self.channel.ircUsers.add('botgotsthis')
        self.channel.ircOps.add('botgotsthis')
        self.channel.onJoin()
        self.assertFalse(self.channel.ircUsers)
        self.assertFalse(self.channel.ircOps)

    def test_part(self):
        self.channel.part()
        self.socket.partChannel.assert_called_once_with(self.channel)
        self.socket.messaging.clearChat.assert_called_once_with(self.channel)

    def test_clear(self):
        self.channel.clear()
        self.socket.messaging.clearChat.assert_called_once_with(self.channel)

    def test_send(self):
        self.channel.send('Kappa')
        self.socket.messaging.sendChat.assert_called_once_with(
            self.channel, 'Kappa', 1)

    def test_send_iterable_priority(self):
        messages = ['Kappa', 'Keepo', 'KappaHD', 'KappaPride', 'KappaRoss',
                    'KappaClaus']
        self.channel.send(messages, 0)
        self.socket.messaging.sendChat.assert_called_once_with(
            self.channel, messages, 0)


class TestChannelAsync(asynctest.TestCase):
    def setUp(self):
        self.socket = Mock(spec=Socket)
        self.socket.messaging = Mock(spec=MessagingQueue)
        self.channel = Channel('botgotsthis', self.socket)

    @patch('bot.utils.now', autospec=True)
    @patch('source.api.ffz.getBroadcasterEmotes')
    async def test_updateFfzEmotes(self, mock_getFfzEmotes, mock_now):
        now = datetime(2000, 1, 1)
        emotes = {-1: 'FrankerFaceZ'}
        mock_now.return_value = now
        mock_getFfzEmotes.return_value = emotes
        await self.channel.updateFfzEmotes()
        mock_getFfzEmotes.assert_called_once_with(self.channel.channel)
        self.assertEqual(self.channel.ffzCache, now)
        self.assertEqual(self.channel.ffzEmotes, emotes)

    @patch('bot.utils.now', autospec=True)
    @patch('source.api.ffz.getBroadcasterEmotes')
    async def test_updateFfzEmotes_empty(self, mock_getFfzEmotes, mock_now):
        now = datetime(2000, 1, 1)
        emotes = {}
        mock_now.return_value = now
        mock_getFfzEmotes.return_value = emotes
        self.channel._ffzEmotes = {-1: 'FrankerFaceZ'}
        await self.channel.updateFfzEmotes()
        mock_getFfzEmotes.assert_called_once_with(self.channel.channel)
        self.assertEqual(self.channel.ffzCache, now)
        self.assertEqual(self.channel.ffzEmotes, emotes)

    @patch('bot.utils.now', autospec=True)
    @patch('source.api.ffz.getBroadcasterEmotes')
    async def test_updateFfzEmotes_error(self, mock_getFfzEmotes, mock_now):
        now = datetime(2000, 1, 1)
        emotes = {-1: 'FrankerFaceZ'}
        self.channel._ffzEmotes = emotes
        mock_now.return_value = now
        mock_getFfzEmotes.return_value = None
        await self.channel.updateFfzEmotes()
        self.assertEqual(self.channel.ffzCache, datetime.min)
        self.assertEqual(self.channel.ffzEmotes, emotes)
