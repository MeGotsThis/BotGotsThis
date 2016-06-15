import unittest
from bot.twitchmessage import IrcMessagePrefix
from bot.twitchmessage._ircprefix import ParsedPrefix


class TestsIrcPrefix(unittest.TestCase):
    def test_constructor_excepts(self):
        self.assertRaises(TypeError, IrcMessagePrefix, servername=1)
        self.assertRaises(TypeError, IrcMessagePrefix, nick=1)
        self.assertRaises(TypeError, IrcMessagePrefix, user=1)
        self.assertRaises(TypeError, IrcMessagePrefix, host=1)
        self.assertRaises(TypeError, IrcMessagePrefix, 1)
        self.assertRaises(TypeError, IrcMessagePrefix, None, 1)
        self.assertRaises(TypeError, IrcMessagePrefix, None, None, 1)
        self.assertRaises(TypeError, IrcMessagePrefix, None, None, None, 1)
        self.assertRaises(ValueError, IrcMessagePrefix, servername='')
        self.assertRaises(ValueError, IrcMessagePrefix, servername='', nick='')
        self.assertRaises(ValueError, IrcMessagePrefix, servername='a', nick='b')
        self.assertRaises(ValueError, IrcMessagePrefix, nick='a', user='')
        self.assertRaises(ValueError, IrcMessagePrefix,
                          nick='a', user='b', host='')
        self.assertRaises(ValueError, IrcMessagePrefix, servername=' ')
        self.assertRaises(ValueError, IrcMessagePrefix, servername='\0')
        self.assertRaises(ValueError, IrcMessagePrefix, servername='\n')
        self.assertRaises(ValueError, IrcMessagePrefix, servername='\r')
        self.assertRaises(ValueError, IrcMessagePrefix, nick=' ')
        self.assertRaises(ValueError, IrcMessagePrefix, nick='\0')
        self.assertRaises(ValueError, IrcMessagePrefix, nick='\n')
        self.assertRaises(ValueError, IrcMessagePrefix, nick='\r')
        self.assertRaises(ValueError, IrcMessagePrefix, nick='a', user=' ')
        self.assertRaises(ValueError, IrcMessagePrefix, nick='a', user='\0')
        self.assertRaises(ValueError, IrcMessagePrefix, nick='a', user='\n')
        self.assertRaises(ValueError, IrcMessagePrefix, nick='a', user='\r')
        self.assertRaises(ValueError, IrcMessagePrefix,
                          nick='a', user='b', host=' ')
        self.assertRaises(ValueError, IrcMessagePrefix,
                          nick='a', user='b', host='\0')
        self.assertRaises(ValueError, IrcMessagePrefix,
                          nick='a', user='b', host='\n')
        self.assertRaises(ValueError, IrcMessagePrefix,
                          nick='a', user='b', host='\r')
        self.assertRaises(ValueError, IrcMessagePrefix, user='a', host='b')
        self.assertRaises(ValueError, IrcMessagePrefix, user='a')
        self.assertRaises(ValueError, IrcMessagePrefix, host='a')

    def test_servername(self):
        prefix = IrcMessagePrefix(servername='localhost')
        self.assertEqual(prefix.servername, 'localhost')
        self.assertIs(prefix.nick, None)
        self.assertIs(prefix.user, None)
        self.assertIs(prefix.host, None)
        self.assertEqual(str(prefix), 'localhost')
        with self.assertRaises(AttributeError):
            prefix.servername = 'localhost'

        prefix = IrcMessagePrefix(servername='127.0.0.1')
        self.assertEqual(prefix.servername, '127.0.0.1')
        self.assertIs(prefix.nick, None)
        self.assertIs(prefix.user, None)
        self.assertIs(prefix.host, None)
        self.assertEqual(str(prefix), '127.0.0.1')

    def test_nick(self):
        prefix = IrcMessagePrefix(nick='BotGotsThis')
        self.assertIs(prefix.servername, None)
        self.assertEqual(prefix.nick, 'BotGotsThis')
        self.assertIs(prefix.user, None)
        self.assertIs(prefix.host, None)
        self.assertEqual(str(prefix), 'BotGotsThis')
        with self.assertRaises(AttributeError):
            prefix.nick = None
        with self.assertRaises(AttributeError):
            prefix.nick = None
        with self.assertRaises(AttributeError):
            prefix.host = None

    def test_nick_user(self):
        prefix = IrcMessagePrefix(nick='MeGotsThis', user='BotGotsThis')
        self.assertIs(prefix.servername, None)
        self.assertEqual(prefix.nick, 'MeGotsThis')
        self.assertEqual(prefix.user, 'BotGotsThis')
        self.assertIs(prefix.host, None)
        self.assertEqual(str(prefix), 'MeGotsThis!BotGotsThis')

    def test_nick_host(self):
        prefix = IrcMessagePrefix(nick='MeGotsThis', host='localhost')
        self.assertIs(prefix.servername, None)
        self.assertEqual(prefix.nick, 'MeGotsThis')
        self.assertIsNone(prefix.user)
        self.assertEqual(prefix.host, 'localhost')
        self.assertEqual(str(prefix), 'MeGotsThis@localhost')

    def test_nick_user_host(self):
        prefix = IrcMessagePrefix(nick='MeGotsThis', user='BotGotsThis',
                                  host='localhost')
        self.assertIs(prefix.servername, None)
        self.assertEqual(prefix.nick, 'MeGotsThis')
        self.assertEqual(prefix.user, 'BotGotsThis')
        self.assertIs(prefix.host, 'localhost')
        self.assertEqual(str(prefix), 'MeGotsThis!BotGotsThis@localhost')

    def test_from(self):
        self.assertRaises(TypeError, IrcMessagePrefix.fromPrefix, None)
        self.assertRaises(TypeError, IrcMessagePrefix.fromPrefix, 1)
        self.assertRaises(TypeError, IrcMessagePrefix.fromPrefix, b'')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, ' ')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, 'a ')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, ' a')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, ' a ')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '.')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, 'a.')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '.a')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix,
                          'a.b!c.d@e.f')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix,
                          'a.b!c.d@e.f')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, 'a\n')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, 'a\r')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, 'a\0')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '!')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '!a')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, 'a!')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '@')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '@a')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, 'a@')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '!@')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, 'a!@')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '!a@')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '!@a')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, 'a!a@')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, 'a!@a')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '!a@a')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '(')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, ')')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, '[')
        self.assertRaises(ValueError, IrcMessagePrefix.fromPrefix, ']')

        self.assertEqual(IrcMessagePrefix.fromPrefix('megotsthis.com'),
                         IrcMessagePrefix(servername='megotsthis.com'))

        self.assertEqual(IrcMessagePrefix.fromPrefix('127.0.0.1'),
                         IrcMessagePrefix(servername='127.0.0.1'))

        self.assertEqual(IrcMessagePrefix.fromPrefix('Kappa'),
                         IrcMessagePrefix(nick='Kappa'))

        self.assertEqual(IrcMessagePrefix.fromPrefix('1'),
                         IrcMessagePrefix(nick='1'))

        self.assertEqual(IrcMessagePrefix.fromPrefix('123abc'),
                         IrcMessagePrefix(nick='123abc'))

        self.assertEqual(IrcMessagePrefix.fromPrefix('Kappa!Keepo'),
                         IrcMessagePrefix(nick='Kappa', user='Keepo'))

        self.assertEqual(IrcMessagePrefix.fromPrefix('Kappa!Keepo@localhost'),
                         IrcMessagePrefix(nick='Kappa', user='Keepo',
                                          host='localhost'))

    def test_parse(self):
        self.assertRaises(TypeError, IrcMessagePrefix.parse, None)
        self.assertRaises(TypeError, IrcMessagePrefix.parse, 1)
        self.assertRaises(TypeError, IrcMessagePrefix.parse, b'')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, ' ')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a ')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, ' a')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, ' a ')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '.')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a.')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '.a')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a.b!c.d@e.f')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a.b!c.d@e.f')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a\n')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a\r')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a\0')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '!')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '!a')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a!')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '@')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '@a')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a@')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '!@')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a!@')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '!a@')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '!@a')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a!a@')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a!@a')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '!a@a')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '(')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, ')')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '[')
        self.assertRaises(ValueError, IrcMessagePrefix.parse, ']')

        self.assertEqual(IrcMessagePrefix.parse('megotsthis.com'),
                         ParsedPrefix('megotsthis.com', None, None, None))

        self.assertEqual(IrcMessagePrefix.parse('127.0.0.1'),
                         ParsedPrefix('127.0.0.1', None, None, None))

        self.assertEqual(IrcMessagePrefix.parse('Kappa'),
                         ParsedPrefix(None, 'Kappa', None, None))

        self.assertEqual(IrcMessagePrefix.parse('1'),
                         ParsedPrefix(None, '1', None, None))

        self.assertEqual(IrcMessagePrefix.parse('123abc'),
                         ParsedPrefix(None, '123abc', None, None))

        self.assertEqual(IrcMessagePrefix.parse('Kappa!Keepo'),
                         ParsedPrefix(None, 'Kappa', 'Keepo', None))

        self.assertEqual(IrcMessagePrefix.parse('Kappa!Keepo@localhost'),
                         ParsedPrefix(None, 'Kappa', 'Keepo', 'localhost'))

        self.assertEqual(IrcMessagePrefix.parse('MeGotsThis!BotGotsThis@megotsthis.com'),
                         ParsedPrefix(None, 'MeGotsThis', 'BotGotsThis', 'megotsthis.com'))

        self.assertEqual(IrcMessagePrefix.parse('botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv'),
                         ParsedPrefix(None, 'botgotsthis', 'botgotsthis', 'botgotsthis.tmi.twitch.tv'))
