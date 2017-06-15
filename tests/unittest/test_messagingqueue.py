import itertools
import math
import unittest
from bot.coroutine.connection import ConnectionHandler
from bot.data import Channel, ChatMessage, MessagingQueue, WhisperMessage
from datetime import datetime, timedelta
from unittest.mock import call, patch


class BaseTestMessagingQueue(unittest.TestCase):
    def setUp(self):
        self.queue = MessagingQueue()
        connection = ConnectionHandler('Twitch.TV', 'irc.twitch.tv', 6667)
        self.bgt_channel = Channel('botgotsthis', connection, -math.inf)
        self.bgt_channel.isMod = False
        self.mgt_channel = Channel('megotsthis', connection, -math.inf)
        self.mgt_channel.isMod = True
        self.mbt_channel = Channel('mebotsthis', connection, -math.inf)
        self.mbt_channel.isMod = False


class TestMessagingQueue(BaseTestMessagingQueue):
    @patch('bot.config', autospec=True)
    def test_ismod_own_channel(self, mock_config):
        mock_config.botnick = 'botgotsthis'
        self.assertIs(MessagingQueue._isMod(self.bgt_channel), True)

    @patch('bot.config', autospec=True)
    def test_ismod_mod_in_channel(self, mock_config):
        mock_config.botnick = 'botgotsthis'
        self.assertIs(MessagingQueue._isMod(self.mgt_channel), True)

    @patch('bot.config', autospec=True)
    def test_ismod_mod_in_channel_and_owner(self, mock_config):
        mock_config.botnick = 'megotsthis'
        self.assertIs(MessagingQueue._isMod(self.mgt_channel), True)

    @patch('bot.config', autospec=True)
    def test_ismod_not_own_(self, mock_config):
        mock_config.botnick = 'botgotsthis'
        self.assertIs(MessagingQueue._isMod(self.mbt_channel), False)

    def test_sendChat_channel_none(self):
        self.assertRaises(TypeError, self.queue.sendChat, None, '')

    def test_sendChat_channel_int(self):
        self.assertRaises(TypeError, self.queue.sendChat, 1, '')

    def test_sendChat_none(self):
        self.assertRaises(TypeError, self.queue.sendChat, self.bgt_channel, None)

    def test_sendChat_int(self):
        self.assertRaises(TypeError, self.queue.sendChat, self.bgt_channel, 1)

    def test_sendChat_str(self):
        self.queue.sendChat(self.bgt_channel, 'Hello Kappa !')
        self.assertFalse(self.queue._chatQueues[0])
        self.assertFalse(self.queue._chatQueues[2])
        self.assertEqual(len(self.queue._chatQueues[1]), 1)
        self.assertIsInstance(self.queue._chatQueues[1][0], ChatMessage)
        self.assertIs(self.queue._chatQueues[1][0].channel, self.bgt_channel)
        self.assertIs(self.queue._chatQueues[1][0].message, 'Hello Kappa !')

    def test_sendChat_list_str(self):
        self.queue.sendChat(self.bgt_channel, ['Kappa ', 'Kappa Kappa ', 'Kappa Kappa Kappa '])
        self.assertFalse(self.queue._chatQueues[0])
        self.assertFalse(self.queue._chatQueues[2])
        self.assertEqual(len(self.queue._chatQueues[1]), 3)
        self.assertIs(self.queue._chatQueues[1][0].message, 'Kappa ')
        self.assertIs(self.queue._chatQueues[1][1].message, 'Kappa Kappa ')
        self.assertIs(self.queue._chatQueues[1][2].message, 'Kappa Kappa Kappa ')

    def test_sendChat_tuple_str(self):
        self.queue.sendChat(self.bgt_channel, ('a', 'b', 'c', 'd'))
        self.assertFalse(self.queue._chatQueues[0])
        self.assertFalse(self.queue._chatQueues[2])
        self.assertEqual(len(self.queue._chatQueues[1]), 4)
        self.assertIs(self.queue._chatQueues[1][0].message, 'a')
        self.assertIs(self.queue._chatQueues[1][1].message, 'b')
        self.assertIs(self.queue._chatQueues[1][2].message, 'c')
        self.assertIs(self.queue._chatQueues[1][3].message, 'd')

    def test_sendChat_generator_str(self):
        self.queue.sendChat(self.bgt_channel, (str(i) for i in range(10)))
        self.assertFalse(self.queue._chatQueues[0])
        self.assertFalse(self.queue._chatQueues[2])
        self.assertEqual(len(self.queue._chatQueues[1]), 10)
        self.assertEqual(self.queue._chatQueues[1][0].message, '0')
        self.assertEqual(self.queue._chatQueues[1][1].message, '1')
        self.assertEqual(self.queue._chatQueues[1][2].message, '2')
        self.assertEqual(self.queue._chatQueues[1][3].message, '3')
        self.assertEqual(self.queue._chatQueues[1][4].message, '4')
        self.assertEqual(self.queue._chatQueues[1][5].message, '5')
        self.assertEqual(self.queue._chatQueues[1][6].message, '6')
        self.assertEqual(self.queue._chatQueues[1][7].message, '7')
        self.assertEqual(self.queue._chatQueues[1][8].message, '8')
        self.assertEqual(self.queue._chatQueues[1][9].message, '9')

    def test_sendChat_generator_int(self):
        self.assertRaises(TypeError, self.queue.sendChat, self.bgt_channel, range(10))
        self.assertFalse(self.queue._chatQueues[0])
        self.assertFalse(self.queue._chatQueues[1])
        self.assertFalse(self.queue._chatQueues[2])

    def test_sendChat_generator_str_int(self):
        self.assertRaises(TypeError, self.queue.sendChat, self.bgt_channel,
                          itertools.chain((str(i) for i in range(10)), range(10)))
        self.assertFalse(self.queue._chatQueues[0])
        self.assertFalse(self.queue._chatQueues[1])
        self.assertFalse(self.queue._chatQueues[2])

    def test_sendChat_multiple_calls(self):
        self.queue.sendChat(self.bgt_channel, 'TBTacoLeft TBCheesePull TBTacoRight ')
        self.queue.sendChat(self.mgt_channel, '<3 :)')
        self.queue.sendChat(self.bgt_channel, 'duDudu duDudu duDudu ')
        self.assertFalse(self.queue._chatQueues[0])
        self.assertFalse(self.queue._chatQueues[2])
        self.assertEqual(len(self.queue._chatQueues[1]), 3)
        self.assertIs(self.queue._chatQueues[1][0].channel, self.bgt_channel)
        self.assertIs(self.queue._chatQueues[1][0].message, 'TBTacoLeft TBCheesePull TBTacoRight ')
        self.assertIs(self.queue._chatQueues[1][1].channel, self.mgt_channel)
        self.assertIs(self.queue._chatQueues[1][1].message, '<3 :)')
        self.assertIs(self.queue._chatQueues[1][2].channel, self.bgt_channel)
        self.assertIs(self.queue._chatQueues[1][2].message, 'duDudu duDudu duDudu ')

    def test_sendChat_highest_priority(self):
        self.queue.sendChat(self.bgt_channel, 'KevinTurtle', 0)
        self.assertFalse(self.queue._chatQueues[1])
        self.assertFalse(self.queue._chatQueues[2])
        self.assertEqual(len(self.queue._chatQueues[0]), 1)
        self.assertIsInstance(self.queue._chatQueues[0][0], ChatMessage)
        self.assertIs(self.queue._chatQueues[0][0].channel, self.bgt_channel)
        self.assertIs(self.queue._chatQueues[0][0].message, 'KevinTurtle')

    def test_sendChat_lowest_priority(self):
        self.queue.sendChat(self.bgt_channel, 'SwiftRage', -1)
        self.assertFalse(self.queue._chatQueues[0])
        self.assertFalse(self.queue._chatQueues[1])
        self.assertEqual(len(self.queue._chatQueues[2]), 1)
        self.assertIsInstance(self.queue._chatQueues[2][0], ChatMessage)
        self.assertIs(self.queue._chatQueues[2][0].channel, self.bgt_channel)
        self.assertIs(self.queue._chatQueues[2][0].message, 'SwiftRage')

    def test_sendChat_priority_out_of_range_positive(self):
        self.assertRaises(ValueError, self.queue.sendChat, self.bgt_channel, 'SwiftRage', len(self.queue._chatQueues))
        self.assertFalse(any(self.queue._chatQueues))

    def test_sendChat_priority_out_of_range_negative(self):
        self.assertRaises(ValueError, self.queue.sendChat, self.bgt_channel, 'SwiftRage', -len(self.queue._chatQueues) - 1)
        self.assertFalse(any(self.queue._chatQueues))

    def test_sendChat_priority_multiple_calls(self):
        self.queue.sendChat(self.bgt_channel, ':)', 1)
        self.queue.sendChat(self.mgt_channel, ';)', 1)
        self.queue.sendChat(self.bgt_channel, ':/', 0)
        self.queue.sendChat(self.mgt_channel, ':(', 2)
        self.assertEqual(len(self.queue._chatQueues[0]), 1)
        self.assertEqual(len(self.queue._chatQueues[1]), 2)
        self.assertEqual(len(self.queue._chatQueues[2]), 1)
        self.assertIs(self.queue._chatQueues[0][0].channel, self.bgt_channel)
        self.assertIs(self.queue._chatQueues[0][0].message, ':/')
        self.assertIs(self.queue._chatQueues[1][0].channel, self.bgt_channel)
        self.assertIs(self.queue._chatQueues[1][0].message, ':)')
        self.assertIs(self.queue._chatQueues[1][1].channel, self.mgt_channel)
        self.assertIs(self.queue._chatQueues[1][1].message, ';)')
        self.assertIs(self.queue._chatQueues[2][0].channel, self.mgt_channel)
        self.assertIs(self.queue._chatQueues[2][0].message, ':(')

    def test_sendChat_disallowed_commands(self):
        self.queue.sendChat(self.bgt_channel, '.disconnect')
        self.queue.sendChat(self.bgt_channel, '/disconnect')
        self.queue.sendChat(self.bgt_channel, '.ignore megotsthis')
        self.queue.sendChat(self.bgt_channel, '/ignore botgotsthis')
        self.assertFalse(any(self.queue._chatQueues))

    def test_sendChat_allow_disallowed_commands(self):
        self.queue.sendChat(self.bgt_channel, '.disconnect', bypass=True)
        self.queue.sendChat(self.bgt_channel, '/disconnect', bypass=True)
        self.queue.sendChat(self.bgt_channel, '.ignore megotsthis', bypass=True)
        self.queue.sendChat(self.bgt_channel, '/ignore botgotsthis', bypass=True)
        self.assertFalse(self.queue._chatQueues[0])
        self.assertFalse(self.queue._chatQueues[2])
        self.assertEqual(len(self.queue._chatQueues[1]), 4)

    @patch.object(MessagingQueue, 'sendWhisper', autospec=True)
    def test_sendChat_whisper(self, mock_sendWhisper):
        self.queue.sendChat(self.bgt_channel, '.w botgotsthis Kappa')
        self.assertFalse(any(self.queue._chatQueues))
        mock_sendWhisper.assert_called_once_with(
            self.queue, 'botgotsthis', ['Kappa'])

    @patch.object(MessagingQueue, 'sendWhisper', autospec=True)
    def test_sendChat_whispers(self, mock_sendWhisper):
        self.queue.sendChat(self.bgt_channel, ['.w botgotsthis Kappa',
                                               '.w megotsthis KappaPride',
                                               '.w mebotsthis KappaClaus'])
        self.assertFalse(any(self.queue._chatQueues))
        mock_sendWhisper.assert_has_calls(
            [call(self.queue, 'botgotsthis', ['Kappa']),
             call(self.queue, 'megotsthis', ['KappaPride']),
             call(self.queue, 'mebotsthis', ['KappaClaus'])])

    @patch.object(MessagingQueue, 'sendWhisper', autospec=True)
    def test_sendChat_whispers_multi(self, mock_sendWhisper):
        self.queue.sendChat(self.bgt_channel, ['.w botgotsthis Kappa',
                                               '.w megotsthis KappaPride',
                                               '.w mebotsthis KappaClaus',
                                               '.w botgotsthis FrankerZ',
                                               '.w megotsthis RalpherZ',
                                               '.w mebotsthis ChefFrank'], 0)
        self.assertFalse(any(self.queue._chatQueues))
        mock_sendWhisper.assert_has_calls(
            [call(self.queue, 'botgotsthis', ['Kappa', 'FrankerZ']),
             call(self.queue, 'megotsthis', ['KappaPride', 'RalpherZ']),
             call(self.queue, 'mebotsthis', ['KappaClaus', 'ChefFrank'])])

    def test_sendWhisper_None(self):
        self.assertRaises(TypeError, self.queue.sendWhisper, None, 'PogChamp')

    def test_sendWhisper_str_None(self):
        self.assertRaises(TypeError,
                          self.queue.sendWhisper, 'botgotsthis', None)

    def test_sendWhisper_str(self):
        self.queue.sendWhisper('botgotsthis', 'PogChamp')
        self.assertEqual(len(self.queue._whisperQueue), 1)
        self.assertEqual(self.queue._whisperQueue[0].nick, 'botgotsthis')
        self.assertEqual(self.queue._whisperQueue[0].message, 'PogChamp')

    def test_sendWhisper_list(self):
        self.queue.sendWhisper('botgotsthis', ['PogChamp', 'KevinTurtle'])
        self.assertEqual(len(self.queue._whisperQueue), 2)
        self.assertEqual(self.queue._whisperQueue[0].nick, 'botgotsthis')
        self.assertEqual(self.queue._whisperQueue[0].message, 'PogChamp')
        self.assertEqual(self.queue._whisperQueue[1].nick, 'botgotsthis')
        self.assertEqual(self.queue._whisperQueue[1].message, 'KevinTurtle')

    def test_sendWhisper_tuple(self):
        self.queue.sendWhisper('botgotsthis', ('PogChamp', 'KevinTurtle'))
        self.assertEqual(len(self.queue._whisperQueue), 2)
        self.assertEqual(self.queue._whisperQueue[0].message, 'PogChamp')
        self.assertEqual(self.queue._whisperQueue[1].message, 'KevinTurtle')

    def test_sendWhisper_generator(self):
        self.queue.sendWhisper('botgotsthis', (str(i) for i in range(3)))
        self.assertEqual(len(self.queue._whisperQueue), 3)
        self.assertEqual(self.queue._whisperQueue[0].message, '0')
        self.assertEqual(self.queue._whisperQueue[1].message, '1')
        self.assertEqual(self.queue._whisperQueue[2].message, '2')

    def test_sendWhisper_multiple_calls(self):
        self.queue.sendWhisper('botgotsthis', 'PraiseIt')
        self.queue.sendWhisper('megotsthis', 'bleedPurple')
        self.assertEqual(len(self.queue._whisperQueue), 2)
        self.assertEqual(self.queue._whisperQueue[0].nick, 'botgotsthis')
        self.assertEqual(self.queue._whisperQueue[0].message, 'PraiseIt')
        self.assertEqual(self.queue._whisperQueue[1].nick, 'megotsthis')
        self.assertEqual(self.queue._whisperQueue[1].message, 'bleedPurple')

    @patch('bot.utils.now', autospec=True)
    @patch('bot.config', autospec=True)
    def test_cleanOldTimestamps(self, mock_config, mock_now):
        # Setup
        now = datetime(2000, 1, 1, 0, 0, 0)
        mock_config.messageSpan = 10
        mock_config.whiperSpan = 10
        mock_now.return_value = now
        self.queue._chatSent.extend(now + i * timedelta(seconds=1) for i in range(-20, 11))
        self.queue._whisperSent.extend(now + i * timedelta(seconds=1.5) for i in range(-10, 11))
        # Call
        self.queue.cleanOldTimestamps()
        # Check
        self.assertCountEqual(self.queue._chatSent, [now + i * timedelta(seconds=1) for i in range(-10, 11)])
        self.assertCountEqual(self.queue._whisperSent, [now + i * timedelta(seconds=1.5) for i in range(-6, 11)])

    def test_clearChat_empty(self):
        self.assertFalse(any(self.queue._chatQueues))
        self.queue.clearChat(self.bgt_channel)
        self.assertFalse(any(self.queue._chatQueues))

    def test_clearChat_single(self):
        self.queue._chatQueues[1].append(ChatMessage(self.bgt_channel, 'Kappa'))
        self.queue.clearChat(self.bgt_channel)
        self.assertFalse(any(self.queue._chatQueues))

    def test_clearChat_multiple(self):
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, '0'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, '1'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, '2'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, '3'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, '4'))
        self.queue.clearChat(self.bgt_channel)
        self.assertFalse(any(self.queue._chatQueues))

    def test_clearChat_mixing(self):
        self.queue._chatQueues[0].append(ChatMessage(self.bgt_channel, 'a'))
        self.queue._chatQueues[0].append(ChatMessage(self.mgt_channel, 'b'))
        self.queue._chatQueues[0].append(ChatMessage(self.mbt_channel, 'c'))
        self.queue._chatQueues[0].append(ChatMessage(self.bgt_channel, 'd'))
        self.queue._chatQueues[0].append(ChatMessage(self.bgt_channel, 'e'))
        self.queue._chatQueues[1].append(ChatMessage(self.mgt_channel, 'f'))
        self.queue._chatQueues[1].append(ChatMessage(self.mbt_channel, 'g'))
        self.queue._chatQueues[1].append(ChatMessage(self.bgt_channel, 'h'))
        self.queue._chatQueues[1].append(ChatMessage(self.bgt_channel, 'i'))
        self.queue._chatQueues[1].append(ChatMessage(self.mbt_channel, 'j'))
        self.queue._chatQueues[1].append(ChatMessage(self.bgt_channel, 'k'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, 'l'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, 'm'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, 'n'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, 'o'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, 'p'))
        self.queue.clearChat(self.bgt_channel)
        self.assertEqual(len(self.queue._chatQueues[0]), 2)
        self.assertEqual(len(self.queue._chatQueues[1]), 3)
        self.assertFalse(self.queue._chatQueues[2])
        self.assertIs(self.queue._chatQueues[0][0].channel, self.mgt_channel)
        self.assertIs(self.queue._chatQueues[0][1].channel, self.mbt_channel)
        self.assertIs(self.queue._chatQueues[1][0].channel, self.mgt_channel)
        self.assertIs(self.queue._chatQueues[1][1].channel, self.mbt_channel)
        self.assertIs(self.queue._chatQueues[1][2].channel, self.mbt_channel)

    def test_clearAllChat(self):
        self.queue._chatQueues[0].append(ChatMessage(self.bgt_channel, 'a'))
        self.queue._chatQueues[0].append(ChatMessage(self.mgt_channel, 'b'))
        self.queue._chatQueues[0].append(ChatMessage(self.mbt_channel, 'c'))
        self.queue._chatQueues[0].append(ChatMessage(self.bgt_channel, 'd'))
        self.queue._chatQueues[0].append(ChatMessage(self.bgt_channel, 'e'))
        self.queue._chatQueues[1].append(ChatMessage(self.mgt_channel, 'f'))
        self.queue._chatQueues[1].append(ChatMessage(self.mbt_channel, 'g'))
        self.queue._chatQueues[1].append(ChatMessage(self.bgt_channel, 'h'))
        self.queue._chatQueues[1].append(ChatMessage(self.bgt_channel, 'i'))
        self.queue._chatQueues[1].append(ChatMessage(self.mbt_channel, 'j'))
        self.queue._chatQueues[1].append(ChatMessage(self.bgt_channel, 'k'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, 'l'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, 'm'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, 'n'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, 'o'))
        self.queue._chatQueues[2].append(ChatMessage(self.bgt_channel, 'p'))
        self.queue.clearAllChat()
        self.assertFalse(any(self.queue._chatQueues))

    @patch('bot.utils.now', autospec=True)
    @patch.object(MessagingQueue, '_getChatMessage', autospec=True)
    def test_popChat_None(self, mock_getChatMessage, mock_now):
        mock_getChatMessage.return_value = None
        now = datetime(2000, 1, 1, 0, 0, 0)
        mock_now.return_value = now
        self.assertIsNone(self.queue.popChat())
        self.assertFalse(self.queue._chatSent)

    @patch('bot.utils.now', autospec=True)
    @patch.object(MessagingQueue, '_getChatMessage', autospec=True)
    def test_popChat(self, mock_getChatMessage, mock_now):
        msg = ChatMessage(self.bgt_channel, 'TBTacoLeft TBCheesePull TBTacoRight')
        mock_getChatMessage.return_value = msg
        now = datetime(2000, 1, 1, 0, 0, 0)
        mock_now.return_value = now
        self.assertIs(self.queue.popChat(), msg)
        self.assertEqual(self.queue._chatSent, [now])

    @patch('bot.utils.now', autospec=True)
    @patch.object(MessagingQueue, '_getChatMessage', autospec=True)
    def test_popWhisper_None(self, mock_getChatMessage, mock_now):
        mock_getChatMessage.return_value = None
        now = datetime(2000, 1, 1, 0, 0, 0)
        mock_now.return_value = now
        self.assertIsNone(self.queue.popWhisper())
        self.assertFalse(self.queue._whisperSent)

    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_popWhisper(self, mock_now, mock_config):
        mock_config.whiperLimit = 5
        msg = WhisperMessage('botgotsthis', 'TBTacoLeft TBCheesePull TBTacoRight')
        self.queue._whisperQueue.append(msg)
        now = datetime(2000, 1, 1, 0, 0, 0)
        mock_now.return_value = now
        self.assertIs(self.queue.popWhisper(), msg)
        self.assertEqual(self.queue._whisperSent, [now])

    @patch('bot.config', autospec=True)
    @patch('bot.utils.now', autospec=True)
    def test_popWhisper_full(self, mock_now, mock_config):
        mock_config.whiperLimit = 5
        msg = WhisperMessage('botgotsthis', 'TBTacoLeft TBCheesePull TBTacoRight')
        self.queue._whisperQueue.append(msg)
        now = datetime(2000, 1, 1, 0, 0, 0)
        mock_now.return_value = now
        self.queue._whisperSent.extend(now for _ in range(5))
        self.assertIsNone(self.queue.popWhisper())
        self.assertEqual(self.queue._whisperSent, [now for _ in range(5)])


class TestMessagingQueueGetChatMessage(BaseTestMessagingQueue):
    def setUp(self):
        super().setUp()
        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.botnick = 'botgotsthis'
        self.mock_config.modLimit = 5
        self.mock_config.modSpamLimit = 5
        self.mock_config.publicLimit = 2
        self.mock_config.publicDelay = 1
        self.mock_config.messageSpan = 10000

        patcher = patch('bot.utils.now', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_now = patcher.start()
        self.now = datetime(2000, 1, 1, 0, 0, 0)
        self.mock_now.return_value = self.now

    def test_empty(self):
        self.assertIsNone(self.queue._getChatMessage(self.now))
        self.assertFalse(self.queue._lowQueueRecent)
        self.assertFalse(self.queue._publicTime)

    def test_full(self):
        self.queue._chatSent.extend(self.now for i in range(5))
        self.queue._whisperSent.extend(self.now for i in range(5))
        self.queue._chatQueues[0].append(ChatMessage(self.bgt_channel, 'PogChamp'))
        self.queue._chatQueues[1].append(ChatMessage(self.mgt_channel, 'Kreygasm'))
        self.queue._chatQueues[2].append(ChatMessage(self.mbt_channel, 'Kappa'))
        self.assertIsNone(self.queue._getChatMessage(self.now))
        self.assertFalse(self.queue._lowQueueRecent)
        self.assertFalse(self.queue._publicTime)

    def test_single_mod(self):
        msg = ChatMessage(self.mgt_channel, 'Kreygasm')
        self.queue._chatQueues[0].append(msg)
        self.assertIs(self.queue._getChatMessage(self.now), msg)
        self.assertFalse(self.queue._lowQueueRecent)
        self.assertEqual(self.queue._publicTime[msg.channel.channel], self.queue._publicTime.default_factory())
        self.assertIsNone(self.queue._getChatMessage(self.now))

    def test_single_notmod(self):
        msg = ChatMessage(self.mbt_channel, 'BionicBunion')
        self.queue._chatQueues[0].append(msg)
        self.assertIs(self.queue._getChatMessage(self.now), msg)
        self.assertFalse(self.queue._lowQueueRecent)
        self.assertEqual(self.queue._publicTime[msg.channel.channel], self.now)

    def test_double(self):
        msg1 = ChatMessage(self.bgt_channel, 'PJSalt')
        msg2 = ChatMessage(self.mgt_channel, 'PJSugar')
        self.queue._chatQueues[0].append(msg1)
        self.queue._chatQueues[0].append(msg2)
        self.assertIs(self.queue._getChatMessage(self.now), msg1)
        self.assertIs(self.queue._getChatMessage(self.now), msg2)

    def test_lowest_priority(self):
        msg = ChatMessage(self.bgt_channel, 'ResidentSleeper')
        self.queue._chatQueues[-1].append(msg)
        self.assertIs(self.queue._getChatMessage(self.now), msg)
        self.assertEqual(self.queue._publicTime[msg.channel.channel], self.queue._publicTime.default_factory())
        self.assertIn(msg.channel.channel, self.queue._lowQueueRecent)

    def test_lowest_priority_nonmod(self):
        msg = ChatMessage(self.mbt_channel, 'OneHand')
        self.queue._chatQueues[-1].append(msg)
        self.assertIs(self.queue._getChatMessage(self.now), msg)
        self.assertFalse(self.queue._lowQueueRecent)
        self.assertEqual(self.queue._publicTime[msg.channel.channel], self.now)

    def test_lowest_priority_multiple(self):
        msgs1 = [ChatMessage(self.bgt_channel, 'KappaRoss') for _ in range(2)]
        msgs2 = [ChatMessage(self.mgt_channel, 'KappaPride') for _ in range(2)]
        self.queue._chatQueues[-1].append(msgs1[0])
        self.queue._chatQueues[-1].extend(msgs2)
        self.queue._chatQueues[-1].append(msgs1[1])
        self.assertIs(self.queue._getChatMessage(self.now), msgs1[0])
        self.assertEqual(list(self.queue._lowQueueRecent),
                         [self.bgt_channel.channel])
        self.assertIs(self.queue._getChatMessage(self.now), msgs2[0])
        self.assertEqual(list(self.queue._lowQueueRecent),
                         [self.bgt_channel.channel, self.mgt_channel.channel])
        self.assertIs(self.queue._getChatMessage(self.now), msgs1[1])
        self.assertEqual(list(self.queue._lowQueueRecent),
                         [self.mgt_channel.channel, self.bgt_channel.channel])
        self.assertIs(self.queue._getChatMessage(self.now), msgs2[1])
        self.assertEqual(list(self.queue._lowQueueRecent),
                         [self.bgt_channel.channel, self.mgt_channel.channel])

    def test_prioirity_top_two_1(self):
        msg1 = ChatMessage(self.bgt_channel, 'CorgiDerp')
        msg2 = ChatMessage(self.bgt_channel, 'OhMyDog')
        self.queue._chatQueues[0].append(msg1)
        self.queue._chatQueues[1].append(msg2)
        self.assertIs(self.queue._getChatMessage(self.now), msg1)
        self.assertIs(self.queue._getChatMessage(self.now), msg2)

    def test_prioirity_top_two_2(self):
        msg1 = ChatMessage(self.bgt_channel, 'BudBlast')
        msg2 = ChatMessage(self.bgt_channel, 'BudStar')
        self.queue._chatQueues[0].append(msg1)
        self.queue._chatQueues[2].append(msg2)
        self.assertIs(self.queue._getChatMessage(self.now), msg1)
        self.assertIs(self.queue._getChatMessage(self.now), msg2)

    def test_prioirity_top_two_3(self):
        msg1 = ChatMessage(self.bgt_channel, 'Kippa')
        msg2 = ChatMessage(self.bgt_channel, 'Keepo')
        self.queue._chatQueues[1].append(msg1)
        self.queue._chatQueues[2].append(msg2)
        self.assertIs(self.queue._getChatMessage(self.now), msg1)
        self.assertIs(self.queue._getChatMessage(self.now), msg2)

    def test_nonmod_mod(self):
        msg1 = ChatMessage(self.bgt_channel, 'KAPOW')
        msg2 = ChatMessage(self.mbt_channel, 'FunRun')
        self.queue._chatQueues[1].append(msg1)
        self.queue._chatQueues[1].append(msg2)
        self.assertIs(self.queue._getChatMessage(self.now), msg2)
        self.assertIs(self.queue._getChatMessage(self.now), msg1)

    def test_prioirity_nonmod_mod(self):
        msg1 = ChatMessage(self.bgt_channel, 'KAPOW')
        msg2 = ChatMessage(self.mbt_channel, 'FunRun')
        self.queue._chatQueues[0].append(msg1)
        self.queue._chatQueues[1].append(msg2)
        self.assertIs(self.queue._getChatMessage(self.now), msg2)
        self.assertIs(self.queue._getChatMessage(self.now), msg1)

    def test_nonmod_semifull(self):
        self.queue._chatSent.extend(self.now for i in range(1))
        msg1 = ChatMessage(self.bgt_channel, 'KAPOW')
        msg2 = ChatMessage(self.mbt_channel, 'FunRun')
        self.queue._chatQueues[1].append(msg1)
        self.queue._chatQueues[1].append(msg2)
        self.assertIs(self.queue._getChatMessage(self.now), msg2)
        self.assertIs(self.queue._getChatMessage(self.now), msg1)

    def test_nonmod_full(self):
        self.queue._chatSent.extend(self.now for i in range(2))
        msg1 = ChatMessage(self.bgt_channel, 'KAPOW')
        msg2 = ChatMessage(self.mbt_channel, 'FunRun')
        self.queue._chatQueues[1].append(msg1)
        self.queue._chatQueues[1].append(msg2)
        self.assertIs(self.queue._getChatMessage(self.now), msg1)
        self.assertIsNone(self.queue._getChatMessage(self.now))
        self.assertIs(self.queue._chatQueues[1][0], msg2)
