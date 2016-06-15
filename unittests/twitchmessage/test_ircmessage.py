import unittest
from bot.twitchmessage import IrcMessage, IrcMessageParams, IrcMessagePrefix
from bot.twitchmessage import IrcMessageTagsKey, IrcMessageTagsReadOnly
from bot.twitchmessage._ircmessage import ParsedMessage


class TestsIrcMessage(unittest.TestCase):
    def test_except(self):
        self.assertRaises(TypeError, IrcMessage, tags=1)
        self.assertRaises(TypeError, IrcMessage, tags='')
        self.assertRaises(TypeError, IrcMessage, tags=b'')
        self.assertRaises(TypeError, IrcMessage, tags=[])
        self.assertRaises(TypeError, IrcMessage, tags={})
        self.assertRaises(TypeError, IrcMessage, prefix=1)
        self.assertRaises(TypeError, IrcMessage, prefix='')
        self.assertRaises(TypeError, IrcMessage, prefix=b'')
        self.assertRaises(TypeError, IrcMessage, prefix=[])
        self.assertRaises(TypeError, IrcMessage, prefix={})
        self.assertRaises(TypeError, IrcMessage, command=b'')
        self.assertRaises(TypeError, IrcMessage, command=[])
        self.assertRaises(TypeError, IrcMessage, command={})
        self.assertRaises(TypeError, IrcMessage, command=None)
        self.assertRaises(TypeError, IrcMessage, params=1)
        self.assertRaises(TypeError, IrcMessage, params='')
        self.assertRaises(TypeError, IrcMessage, params=b'')
        self.assertRaises(TypeError, IrcMessage, params=[])
        self.assertRaises(TypeError, IrcMessage, params={})
        self.assertRaises(TypeError, IrcMessage, params=None)

    def test_command(self):
        message = IrcMessage(command='RECONNECT')
        self.assertIsNone(message.tags)
        self.assertIsNone(message.prefix)
        self.assertEqual(message.command, 'RECONNECT')
        self.assertIs(message.params.isEmpty, True)
        self.assertEqual(str(message), 'RECONNECT')
        self.assertEqual(message, IrcMessage(command='RECONNECT'))
        self.assertNotEqual(message, IrcMessage(command=0))
        with self.assertRaises(AttributeError):
            message.tags = IrcMessageTagsReadOnly()
        with self.assertRaises(AttributeError):
            message.prefix = IrcMessageTagsReadOnly()
        with self.assertRaises(AttributeError):
            message.command = IrcMessageTagsReadOnly()
        with self.assertRaises(AttributeError):
            message.params = IrcMessageParams()

    def test_command_params(self):
        message = IrcMessage(command='JOIN',
                             params=IrcMessageParams('#botgotsthis'))
        self.assertIsNone(message.tags)
        self.assertIsNone(message.prefix)
        self.assertEqual(message.command, 'JOIN')
        self.assertIs(message.params.middle, '#botgotsthis')
        self.assertIs(message.params.trailing, None)
        self.assertEqual(str(message), 'JOIN #botgotsthis')
        self.assertEqual(message,
                         IrcMessage(command='JOIN',
                                    params=IrcMessageParams('#botgotsthis')))
        self.assertNotEqual(message,
                            IrcMessage(command='JOIN',
                                       params=IrcMessageParams('#megotsthis')))

        message = IrcMessage(command='PRIVMSG',
                             params=IrcMessageParams('#botgotsthis', 'Hello World'))
        self.assertIsNone(message.tags)
        self.assertIsNone(message.prefix)
        self.assertEqual(message.command, 'PRIVMSG')
        self.assertIs(message.params.middle, '#botgotsthis')
        self.assertIs(message.params.trailing, 'Hello World')
        self.assertEqual(str(message), 'PRIVMSG #botgotsthis :Hello World')
        self.assertEqual(message,
                         IrcMessage(command='PRIVMSG',
                                    params=IrcMessageParams('#botgotsthis',
                                                            'Hello World')))
        self.assertNotEqual(message,
                            IrcMessage(command='PRIVMSG',
                                       params=IrcMessageParams('#botgotsthis',
                                                               'Hello World!')))

    def test_prefix_command_params(self):
        message = IrcMessage(prefix=IrcMessagePrefix(nick='botgotsthis',
                                                     user='botgotsthis',
                                                     host='botgotsthis.tmi.twitch.tv'),
                             command='PART',
                             params=IrcMessageParams('#botgotsthis'))
        self.assertIsNone(message.tags)
        self.assertIsNone(message.prefix.servername)
        self.assertEqual(message.prefix.nick, 'botgotsthis')
        self.assertEqual(message.prefix.user, 'botgotsthis')
        self.assertEqual(message.prefix.host, 'botgotsthis.tmi.twitch.tv')
        self.assertEqual(message.command, 'PART')
        self.assertIs(message.params.middle, '#botgotsthis')
        self.assertIs(message.params.trailing, None)
        self.assertEqual(str(message), ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv PART #botgotsthis')
        self.assertEqual(message,
                         IrcMessage(prefix=IrcMessagePrefix(nick='botgotsthis',
                                                            user='botgotsthis',
                                                            host='botgotsthis.tmi.twitch.tv'),
                                    command='PART',
                                    params=IrcMessageParams('#botgotsthis')))
        self.assertNotEqual(message,
                         IrcMessage(prefix=IrcMessagePrefix(nick='megotsthis',
                                                            user='megotsthis',
                                                            host='megotsthis.tmi.twitch.tv'),
                                    command='PART',
                                    params=IrcMessageParams('#botgotsthis')))

    def test_tags_prefix_command_params(self):
        message = IrcMessage(
            tags=IrcMessageTagsReadOnly({
                'broadcaster-lang': '',
                'emote-only': '0',
                'r9k': '0',
                'slow': '0',
                'subs-only': '0'
                }),
            prefix=IrcMessagePrefix(servername='tmi.twitch.tv'),
            command='ROOMSTATE', params=IrcMessageParams('#botgotsthis'))
        self.assertEqual(len(message.tags), 5)
        self.assertEqual(message.tags['broadcaster-lang'], '')
        self.assertEqual(message.tags['emote-only'], '0')
        self.assertEqual(message.tags['r9k'], '0')
        self.assertEqual(message.tags['slow'], '0')
        self.assertEqual(message.tags['subs-only'], '0')
        self.assertEqual(message.prefix.servername, 'tmi.twitch.tv')
        self.assertIsNone(message.prefix.nick)
        self.assertIsNone(message.prefix.user)
        self.assertIsNone(message.prefix.host)
        self.assertEqual(message.command, 'ROOMSTATE')
        self.assertIs(message.params.middle, '#botgotsthis')
        self.assertIs(message.params.trailing, None)
        self.assertEqual(str(message), '@' + str(message.tags) + ' :tmi.twitch.tv ROOMSTATE #botgotsthis')
        self.assertEqual(
            message,
            IrcMessage(
                tags=IrcMessageTagsReadOnly({
                    'broadcaster-lang': '',
                    'emote-only': '0',
                    'r9k': '0',
                    'slow': '0',
                    'subs-only': '0'
                    }),
                prefix=IrcMessagePrefix(servername='tmi.twitch.tv'),
                command='ROOMSTATE',
                params=IrcMessageParams('#botgotsthis')))
        self.assertNotEqual(
            message,
            IrcMessage(
                tags=IrcMessageTagsReadOnly({
                    'broadcaster-lang': '',
                    'emote-only': '1',
                    'r9k': '0',
                    'slow': '0',
                    'subs-only': '0'
                    }),
                prefix=IrcMessagePrefix(servername='tmi.twitch.tv'),
                command='ROOMSTATE',
                params=IrcMessageParams('#botgotsthis')))

    def test_parse(self):
        self.assertRaises(TypeError, IrcMessage.parse, None)
        self.assertRaises(TypeError, IrcMessage.parse, 0)
        self.assertRaises(TypeError, IrcMessage.parse, [])
        self.assertRaises(TypeError, IrcMessage.parse, {})
        self.assertRaises(TypeError, IrcMessage.parse, b'')
        self.assertRaises(ValueError, IrcMessage.parse, '')
        self.assertRaises(ValueError, IrcMessage.parse, ' ')
        self.assertRaises(ValueError, IrcMessage.parse, ' ABC')
        self.assertRaises(ValueError, IrcMessage.parse, '\t')
        self.assertRaises(ValueError, IrcMessage.parse, '\n')
        self.assertRaises(ValueError, IrcMessage.parse, '\r')
        self.assertRaises(ValueError, IrcMessage.parse, '\0')
        self.assertRaises(ValueError, IrcMessage.parse, '1')
        self.assertRaises(ValueError, IrcMessage.parse, '01')
        self.assertRaises(ValueError, IrcMessage.parse, '0001')
        self.assertRaises(ValueError, IrcMessage.parse, 'COMMAND_UNDERSCORE')
        self.assertRaises(ValueError, IrcMessage.parse, '@only-tag-here')
        self.assertRaises(ValueError, IrcMessage.parse, '@only-tag-here;with-a-space ')
        self.assertRaises(ValueError, IrcMessage.parse, ':prefix.only')
        self.assertRaises(ValueError, IrcMessage.parse, ':prefix!only@here')
        self.assertRaises(ValueError, IrcMessage.parse, ':prefix.need.a.space ')
        self.assertRaises(ValueError, IrcMessage.parse, '!invalid starting char')
        self.assertRaises(ValueError, IrcMessage.parse, '#invalid starting char')
        self.assertRaises(ValueError, IrcMessage.parse, '$invalid starting char')
        self.assertRaises(ValueError, IrcMessage.parse, '@ 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@\0 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@\r 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@\n 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@( 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@) 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@[ 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@] 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@a! 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@a& 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@a!= 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@a=\n 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@a=\r 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@a=\\ 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@a=\0 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@; 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@a; 001')
        self.assertRaises(ValueError, IrcMessage.parse, '@;a 001')
        self.assertRaises(ValueError, IrcMessage.parse, ': 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':! 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':!a 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':a! 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':@ 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':a@ 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':@a 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':!@ 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':a!@ 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':!a@ 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':!@a 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':a!a@ 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':a!@a 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':!a@a 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':a. 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':.a 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':( 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':) 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':[ 001')
        self.assertRaises(ValueError, IrcMessage.parse, ':] 001')
        self.assertRaises(ValueError, IrcMessage.parse, '001 \0')
        self.assertRaises(ValueError, IrcMessage.parse, '001 \r')
        self.assertRaises(ValueError, IrcMessage.parse, '001 \n')
        self.assertRaises(ValueError, IrcMessage.parse, '001 :\0')
        self.assertRaises(ValueError, IrcMessage.parse, '001 :\r')
        self.assertRaises(ValueError, IrcMessage.parse, '001 :\n')

        self.assertEquals(IrcMessage.parse('RECONNECT'),
                          ParsedMessage(None, None, 'RECONNECT',
                                        IrcMessageParams()))

        self.assertEquals(IrcMessage.parse('PART #botgotsthis'),
                          ParsedMessage(None, None, 'PART',
                                        IrcMessageParams('#botgotsthis')))

        self.assertEquals(IrcMessage.parse(':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv JOIN #botgotsthis'),
                          ParsedMessage(None,
                                        IrcMessagePrefix(nick='botgotsthis',
                                                         user='botgotsthis',
                                                         host='botgotsthis.tmi.twitch.tv'),
                                        'JOIN',
                                        IrcMessageParams('#botgotsthis')))

        self.assertEquals(IrcMessage.parse(':tmi.twitch.tv PONG tmi.twitch.tv :botgotsthis'),
                          ParsedMessage(None,
                                        IrcMessagePrefix(servername='tmi.twitch.tv'),
                                        'PONG',
                                        IrcMessageParams('tmi.twitch.tv',
                                                         'botgotsthis')))

        self.assertEquals(IrcMessage.parse('TEST middle empty trail :'),
                          ParsedMessage(None, None, 'TEST',
                                        IrcMessageParams('middle empty trail', '')))


        self.assertEquals(IrcMessage.parse('TEST :empty middle'),
                          ParsedMessage(None, None, 'TEST',
                                        IrcMessageParams(None, 'empty middle')))

        self.assertEquals(
            IrcMessage.parse(
                '@multiple=spaces  :will!be@used  HERE  to  test :if  this  passes'),
            ParsedMessage(
                IrcMessageTagsReadOnly({'multiple': 'spaces'}),
                IrcMessagePrefix(nick='will', user='be', host='used'),
                'HERE', IrcMessageParams('to test', 'if  this  passes')))

    def test_from(self):
        self.assertRaises(TypeError, IrcMessage.fromMessage, None)
        self.assertRaises(TypeError, IrcMessage.fromMessage, 0)
        self.assertRaises(TypeError, IrcMessage.fromMessage, [])
        self.assertRaises(TypeError, IrcMessage.fromMessage, {})
        self.assertRaises(TypeError, IrcMessage.fromMessage, b'')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ' ')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ' ABC')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '\t')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '\n')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '\r')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '\0')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '1')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '01')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '0001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, 'COMMAND_UNDERSCORE')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@only-tag-here')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@only-tag-here;with-a-space ')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':prefix.only')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':prefix!only@here')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':prefix.need.a.space ')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '!invalid starting char')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '#invalid starting char')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '$invalid starting char')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@ 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@\0 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@\r 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@\n 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@( 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@) 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@[ 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@] 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@a! 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@a& 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@a!= 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@a=\n 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@a=\r 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@a=\\ 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@a=\0 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@; 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@a; 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '@;a 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ': 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':! 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':!a 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':a! 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':@ 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':a@ 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':@a 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':!@ 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':a!@ 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':!a@ 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':!@a 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':a!a@ 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':a!@a 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':!a@a 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':a. 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':.a 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':( 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':) 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':[ 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, ':] 001')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '001 \0')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '001 \r')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '001 \n')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '001 :\0')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '001 :\r')
        self.assertRaises(ValueError, IrcMessage.fromMessage, '001 :\n')

        message = IrcMessage.fromMessage('RECONNECT')
        self.assertIsNone(message.tags)
        self.assertIsNone(message.prefix)
        self.assertEqual(message.command, 'RECONNECT')
        self.assertIs(message.params.isEmpty, True)

        message = IrcMessage.fromMessage('PART #botgotsthis')
        self.assertIsNone(message.tags)
        self.assertIsNone(message.prefix)
        self.assertEqual(message.command, 'PART')
        self.assertEqual(message.params.middle, '#botgotsthis')
        self.assertIsNone(message.params.trailing)

        message = IrcMessage.fromMessage(':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv JOIN #botgotsthis')
        self.assertIsNone(message.tags)
        self.assertIsNone(message.prefix.servername)
        self.assertEqual(message.prefix.nick, 'botgotsthis')
        self.assertEqual(message.prefix.user, 'botgotsthis')
        self.assertEqual(message.prefix.host, 'botgotsthis.tmi.twitch.tv')
        self.assertEqual(message.command, 'JOIN')
        self.assertEqual(message.params.middle, '#botgotsthis')
        self.assertIsNone(message.params.trailing)

        message = IrcMessage.fromMessage(':tmi.twitch.tv PONG tmi.twitch.tv :botgotsthis')
        self.assertIsNone(message.tags)
        self.assertEqual(message.prefix.servername, 'tmi.twitch.tv')
        self.assertIsNone(message.prefix.nick)
        self.assertIsNone(message.prefix.user)
        self.assertIsNone(message.prefix.host)
        self.assertEqual(message.command, 'PONG')
        self.assertEqual(message.params.middle, 'tmi.twitch.tv')
        self.assertEqual(message.params.trailing, 'botgotsthis')

        message = IrcMessage.fromMessage('TEST middle empty trail :')
        self.assertIsNone(message.tags)
        self.assertIsNone(message.prefix)
        self.assertEqual(message.command, 'TEST')
        self.assertEqual(message.params.middle, 'middle empty trail')
        self.assertEqual(message.params.trailing, '')


        message = IrcMessage.fromMessage('TEST :empty middle')
        self.assertIsNone(message.tags)
        self.assertIsNone(message.prefix)
        self.assertEqual(message.command, 'TEST')
        self.assertEqual(message.params.middle, None)
        self.assertEqual(message.params.trailing, 'empty middle')

        message = IrcMessage.fromMessage(
            '@multiple=spaces  :will!be@used  HERE  to  test :if  this  passes')
        self.assertEqual(len(message.tags), 1)
        self.assertEqual(message.tags[IrcMessageTagsKey('multiple')], 'spaces')
        self.assertIsNone(message.prefix.servername)
        self.assertEqual(message.prefix.nick, 'will')
        self.assertEqual(message.prefix.user, 'be')
        self.assertEqual(message.prefix.host, 'used')
        self.assertEqual(message.command, 'HERE')
        self.assertEqual(message.params.middle, 'to test')
        self.assertEqual(message.params.trailing, 'if  this  passes')

        message = IrcMessage.fromMessage(
            '@badges=broadcaster/1;color=#DAA520;display-name=BotGotsThis;'
            'emotes=25:6-10;mod=1;room-id=42553092;subscriber=0;turbo=0;'
            'user-id=55612319;user-type=mod '
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv '
            'PRIVMSG #botgotsthis :Hello Kappa')
        self.assertEqual(len(message.tags), 10)
        self.assertEqual(message.tags['badges'], 'broadcaster/1')
        self.assertEqual(message.tags['color'], '#DAA520')
        self.assertEqual(message.tags['display-name'], 'BotGotsThis')
        self.assertEqual(message.tags['emotes'], '25:6-10')
        self.assertEqual(message.tags['mod'], '1')
        self.assertEqual(message.tags['room-id'], '42553092')
        self.assertEqual(message.tags['turbo'], '0')
        self.assertEqual(message.tags['subscriber'], '0')
        self.assertEqual(message.tags['user-id'], '55612319')
        self.assertEqual(message.tags['user-type'], 'mod')
        self.assertIsNone(message.prefix.servername)
        self.assertEqual(message.prefix.nick, 'botgotsthis')
        self.assertEqual(message.prefix.user, 'botgotsthis')
        self.assertEqual(message.prefix.host, 'botgotsthis.tmi.twitch.tv')
        self.assertEqual(message.command, 'PRIVMSG')
        self.assertEqual(message.params.middle, '#botgotsthis')
        self.assertEqual(message.params.trailing, 'Hello Kappa')

        message = IrcMessage.fromMessage(':tmi.twitch.tv 001 botgotsthis :Welcome, GLHF!')
        self.assertIsNone(message.tags)
        self.assertEqual(message.prefix.servername, 'tmi.twitch.tv')
        self.assertIsNone(message.prefix.nick)
        self.assertIsNone(message.prefix.user)
        self.assertIsNone(message.prefix.host)
        self.assertEqual(message.command, 1)
        self.assertEqual(message.params.middle, 'botgotsthis')
        self.assertEqual(message.params.trailing, 'Welcome, GLHF!')
