import unittest
from bot.twitchmessage import IrcMessagePrefix
from bot.twitchmessage._ircprefix import ParsedPrefix


class TestsIrcPrefix(unittest.TestCase):
    def test_servername_int(self):
        self.assertRaises(TypeError, IrcMessagePrefix, servername=1)
        self.assertRaises(TypeError, IrcMessagePrefix, 1)

    def test_nick_int(self):
        self.assertRaises(TypeError, IrcMessagePrefix, nick=1)
        self.assertRaises(TypeError, IrcMessagePrefix, None, 1)

    def test_user_int(self):
        self.assertRaises(TypeError, IrcMessagePrefix, user=1)
        self.assertRaises(TypeError, IrcMessagePrefix, None, None, 1)

    def test_host_int(self):
        self.assertRaises(TypeError, IrcMessagePrefix, host=1)
        self.assertRaises(TypeError, IrcMessagePrefix, None, None, None, 1)

    def test_empty_servername(self):
        self.assertRaises(ValueError, IrcMessagePrefix, servername='')

    def test_empty_servername_empty_nick(self):
        self.assertRaises(ValueError, IrcMessagePrefix, servername='', nick='')

    def test_servername_nick(self):
        self.assertRaises(ValueError, IrcMessagePrefix, servername='a', nick='b')

    def test_nick_empty_user(self):
        self.assertRaises(ValueError, IrcMessagePrefix, nick='a', user='')

    def test_nick_user_empty_host(self):
        self.assertRaises(ValueError, IrcMessagePrefix,
                          nick='a', user='b', host='')

    def test_servername_space(self):
        self.assertRaises(ValueError, IrcMessagePrefix, servername=' ')

    def test_servername_null_char(self):
        self.assertRaises(ValueError, IrcMessagePrefix, servername='\0')

    def test_servername_nl(self):
        self.assertRaises(ValueError, IrcMessagePrefix, servername='\n')

    def test_servername_cr(self):
        self.assertRaises(ValueError, IrcMessagePrefix, servername='\r')

    def test_nick_space(self):
        self.assertRaises(ValueError, IrcMessagePrefix, nick=' ')

    def test_nick_null_byte(self):
        self.assertRaises(ValueError, IrcMessagePrefix, nick='\0')

    def test_nick_nl(self):
        self.assertRaises(ValueError, IrcMessagePrefix, nick='\n')

    def test_nick_cr(self):
        self.assertRaises(ValueError, IrcMessagePrefix, nick='\r')

    def test_nick_user_space(self):
        self.assertRaises(ValueError, IrcMessagePrefix, nick='a', user=' ')

    def test_nick_user_null_byte(self):
        self.assertRaises(ValueError, IrcMessagePrefix, nick='a', user='\0')

    def test_nick_user_nl(self):
        self.assertRaises(ValueError, IrcMessagePrefix, nick='a', user='\n')

    def test_nick_user_cr(self):
        self.assertRaises(ValueError, IrcMessagePrefix, nick='a', user='\r')

    def test_nick_user_host_space(self):
        self.assertRaises(ValueError, IrcMessagePrefix,
                          nick='a', user='b', host=' ')

    def test_nick_user_host_null_char(self):
        self.assertRaises(ValueError, IrcMessagePrefix,
                          nick='a', user='b', host='\0')

    def test_nick_user_host_nl(self):
        self.assertRaises(ValueError, IrcMessagePrefix,
                          nick='a', user='b', host='\n')

    def test_nick_user_host_cr(self):
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
        self.assertEqual(prefix, IrcMessagePrefix('localhost'))

    def test_set_servername(self):
        prefix = IrcMessagePrefix(servername='localhost')
        with self.assertRaises(AttributeError):
            prefix.servername = 'localhost'

    def test_servername_ip_address(self):
        prefix = IrcMessagePrefix(servername='127.0.0.1')
        self.assertEqual(prefix.servername, '127.0.0.1')
        self.assertIs(prefix.nick, None)
        self.assertIs(prefix.user, None)
        self.assertIs(prefix.host, None)
        self.assertEqual(prefix, IrcMessagePrefix('127.0.0.1'))

    def test_nick(self):
        prefix = IrcMessagePrefix(nick='BotGotsThis')
        self.assertIs(prefix.servername, None)
        self.assertEqual(prefix.nick, 'BotGotsThis')
        self.assertIs(prefix.user, None)
        self.assertIs(prefix.host, None)
        self.assertEqual(prefix, IrcMessagePrefix(None, 'BotGotsThis'))

    def test_set_nick(self):
        prefix = IrcMessagePrefix(nick='BotGotsThis')
        with self.assertRaises(AttributeError):
            prefix.nick = None

    def test_set_user(self):
        prefix = IrcMessagePrefix(nick='BotGotsThis')
        with self.assertRaises(AttributeError):
            prefix.user = 'MeGotsThis'

    def test_set_host(self):
        prefix = IrcMessagePrefix(nick='BotGotsThis')
        with self.assertRaises(AttributeError):
            prefix.host = 'localhost'

    def test_nick_user(self):
        prefix = IrcMessagePrefix(nick='MeGotsThis', user='BotGotsThis')
        self.assertIs(prefix.servername, None)
        self.assertEqual(prefix.nick, 'MeGotsThis')
        self.assertEqual(prefix.user, 'BotGotsThis')
        self.assertIs(prefix.host, None)
        self.assertEqual(prefix, IrcMessagePrefix(None, 'MeGotsThis', 'BotGotsThis'))

    def test_nick_host(self):
        prefix = IrcMessagePrefix(nick='MeGotsThis', host='localhost')
        self.assertIs(prefix.servername, None)
        self.assertEqual(prefix.nick, 'MeGotsThis')
        self.assertIsNone(prefix.user)
        self.assertEqual(prefix.host, 'localhost')
        self.assertEqual(prefix, IrcMessagePrefix(None, 'MeGotsThis', None, 'localhost'))

    def test_nick_user_host(self):
        prefix = IrcMessagePrefix(nick='MeGotsThis', user='BotGotsThis',
                                  host='localhost')
        self.assertIs(prefix.servername, None)
        self.assertEqual(prefix.nick, 'MeGotsThis')
        self.assertEqual(prefix.user, 'BotGotsThis')
        self.assertIs(prefix.host, 'localhost')
        self.assertEqual(prefix, IrcMessagePrefix(None, 'MeGotsThis', 'BotGotsThis', 'localhost'))

    def test_str_magic_servername(self):
        prefix = IrcMessagePrefix(servername='localhost')
        self.assertEqual(str(prefix), 'localhost')

    def test_str_magic_servername_ip_address(self):
        prefix = IrcMessagePrefix(servername='127.0.0.1')
        self.assertEqual(str(prefix), '127.0.0.1')

    def test_str_magic_nick(self):
        prefix = IrcMessagePrefix(nick='BotGotsThis')
        self.assertEqual(str(prefix), 'BotGotsThis')

    def test_str_magic_nick_user(self):
        prefix = IrcMessagePrefix(nick='MeGotsThis', user='BotGotsThis')
        self.assertEqual(str(prefix), 'MeGotsThis!BotGotsThis')

    def test_str_magic_nick_host(self):
        prefix = IrcMessagePrefix(nick='MeGotsThis', host='localhost')
        self.assertEqual(str(prefix), 'MeGotsThis@localhost')

    def test_str_magic_nick_user_host(self):
        prefix = IrcMessagePrefix(nick='MeGotsThis', user='BotGotsThis',
                                  host='localhost')
        self.assertEqual(str(prefix), 'MeGotsThis!BotGotsThis@localhost')

    def test_from_servername(self):
        self.assertEqual(IrcMessagePrefix.fromPrefix('megotsthis.com'),
                         IrcMessagePrefix(servername='megotsthis.com'))

    def test_from_nick(self):
        self.assertEqual(IrcMessagePrefix.fromPrefix('Kappa'),
                         IrcMessagePrefix(nick='Kappa'))

    def test_from_nick_user(self):
        self.assertEqual(IrcMessagePrefix.fromPrefix('Kappa!Keepo'),
                         IrcMessagePrefix(nick='Kappa', user='Keepo'))

    def test_from_nick_user_host(self):
        self.assertEqual(IrcMessagePrefix.fromPrefix('Kappa@localhost'),
                         IrcMessagePrefix(nick='Kappa', host='localhost'))

    def test_from_nick_host(self):
        self.assertEqual(IrcMessagePrefix.fromPrefix('Kappa!Keepo@localhost'),
                         IrcMessagePrefix(nick='Kappa', user='Keepo',
                                          host='localhost'))

    def test_parse_none(self):
        self.assertRaises(TypeError, IrcMessagePrefix.parse, None)

    def test_parse_int(self):
        self.assertRaises(TypeError, IrcMessagePrefix.parse, 1)

    def test_parse_bytes(self):
        self.assertRaises(TypeError, IrcMessagePrefix.parse, b'')

    def test_parse_empty(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '')

    def test_parse_space(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, ' ')

    def test_parse_trailing_space(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a ')

    def test_parse_leading_space(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, ' a')

    def test_parse_covering_space(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, ' a ')

    def test_parse_period(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '.')

    def test_parse_trailing_period(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a.')

    def test_parse_leading_perios(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '.a')

    def test_parse_period_nick(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a.b!c')

    def test_parse_nl(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '\n')

    def test_parse_cr(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '\r')

    def test_parse_null_char(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '\0')

    def test_parse_empty_nick_user(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '!')

    def test_parse_empty_nick_some_user(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '!a')

    def test_parse_some_nick_empty_user(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a!')

    def test_parse_empty_nick_host(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '@')

    def test_parse_empty_nick_some_host(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '@a')

    def test_parse_some_nick_empty_host(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a@')

    def test_parse_empty_nick_user_host(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '!@')

    def test_parse_some_nick_empty_user_host(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a!@')

    def test_parse_some_user_empty_nick_host(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '!a@')

    def test_parse_some_host_empty_nick_user(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '!@a')

    def test_parse_some_nick_user_empty_host(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a!a@')

    def test_parse_some_nick_host_empty_user(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, 'a!@a')

    def test_parse_some_user_host_empty_nick(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '!a@a')

    def test_parse_opeing_parenthesis(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '(')

    def test_parse_closing_parenthesis(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, ')')

    def test_parse_opening_bracket(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, '[')

    def test_parse_closing_bracket(self):
        self.assertRaises(ValueError, IrcMessagePrefix.parse, ']')

    def test_parse_servername(self):
        self.assertEqual(IrcMessagePrefix.parse('megotsthis.com'),
                         ParsedPrefix('megotsthis.com', None, None, None))

    def test_parse_servername_ip_addr(self):
        self.assertEqual(IrcMessagePrefix.parse('127.0.0.1'),
                         ParsedPrefix('127.0.0.1', None, None, None))

    def test_parse_nick(self):
        self.assertEqual(IrcMessagePrefix.parse('Kappa'),
                         ParsedPrefix(None, 'Kappa', None, None))

    def test_parse_nick_number(self):
        self.assertEqual(IrcMessagePrefix.parse('1'),
                         ParsedPrefix(None, '1', None, None))

    def test_parse_nick_number_alpha(self):
        self.assertEqual(IrcMessagePrefix.parse('123abc'),
                         ParsedPrefix(None, '123abc', None, None))

    def test_parse_nick_user(self):
        self.assertEqual(IrcMessagePrefix.parse('Kappa!Keepo'),
                         ParsedPrefix(None, 'Kappa', 'Keepo', None))

    def test_parse_nick_host(self):
        self.assertEqual(IrcMessagePrefix.parse('Kappa@localhost'),
                         ParsedPrefix(None, 'Kappa', None, 'localhost'))

    def test_parse_nick_user_host(self):
        self.assertEqual(IrcMessagePrefix.parse('Kappa!Keepo@localhost'),
                         ParsedPrefix(None, 'Kappa', 'Keepo', 'localhost'))

    def test_parse_nick_user_host_2(self):
        self.assertEqual(IrcMessagePrefix.parse('MeGotsThis!BotGotsThis@megotsthis.com'),
                         ParsedPrefix(None, 'MeGotsThis', 'BotGotsThis', 'megotsthis.com'))

    def test_parse_from_twitch(self):
        self.assertEqual(IrcMessagePrefix.parse('botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv'),
                         ParsedPrefix(None, 'botgotsthis', 'botgotsthis', 'botgotsthis.tmi.twitch.tv'))
