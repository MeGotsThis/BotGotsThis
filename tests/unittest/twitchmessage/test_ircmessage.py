import unittest
from bot.twitchmessage import IrcMessage, IrcMessageParams, IrcMessagePrefix
from bot.twitchmessage import IrcMessageTagsReadOnly
from bot.twitchmessage._ircmessage import ParsedMessage


class TestsIrcMessage(unittest.TestCase):
    def test_constructor_tags_int(self):
        self.assertRaises(TypeError, IrcMessage, tags=1)

    def test_constructor_tags_str(self):
        self.assertRaises(TypeError, IrcMessage, tags='')

    def test_constructor_tags_bytes(self):
        self.assertRaises(TypeError, IrcMessage, tags=b'')

    def test_constructor_tags_list(self):
        self.assertRaises(TypeError, IrcMessage, tags=[])

    def test_constructor_tags_dict(self):
        self.assertRaises(TypeError, IrcMessage, tags={})

    def test_constructor_prefix(self):
        self.assertRaises(TypeError, IrcMessage, prefix=1)

    def test_constructor_prefix_str(self):
        self.assertRaises(TypeError, IrcMessage, prefix='')

    def test_constructor_prefix_bytes(self):
        self.assertRaises(TypeError, IrcMessage, prefix=b'')

    def test_constructor_prefix_list(self):
        self.assertRaises(TypeError, IrcMessage, prefix=[])

    def test_constructor_prefix_dict(self):
        self.assertRaises(TypeError, IrcMessage, prefix={})

    def test_constructor_command_none(self):
        self.assertRaises(TypeError, IrcMessage, command=None)

    def test_constructor_command_empty_str(self):
        self.assertRaises(ValueError, IrcMessage, command='')

    def test_constructor_command_bytes(self):
        self.assertRaises(TypeError, IrcMessage, command=b'')

    def test_constructor_command_list(self):
        self.assertRaises(TypeError, IrcMessage, command=[])

    def test_constructor_command_dict(self):
        self.assertRaises(TypeError, IrcMessage, command={})

    def test_constructor_params_none(self):
        self.assertRaises(TypeError, IrcMessage, params=None)

    def test_constructor_params(self):
        self.assertRaises(TypeError, IrcMessage, params=1)

    def test_constructor_params_str(self):
        self.assertRaises(TypeError, IrcMessage, params='')

    def test_constructor_params_bytes(self):
        self.assertRaises(TypeError, IrcMessage, params=b'')

    def test_constructor_params_list(self):
        self.assertRaises(TypeError, IrcMessage, params=[])

    def test_constructor_params_dict(self):
        self.assertRaises(TypeError, IrcMessage, params={})

    def test_command_set_tags(self):
        message = IrcMessage(command=0)
        with self.assertRaises(AttributeError):
            message.tags = IrcMessageTagsReadOnly()

    def test_command_set_prefix(self):
        message = IrcMessage(command=0)
        with self.assertRaises(AttributeError):
            message.prefix = IrcMessageTagsReadOnly()

    def test_command_set_command(self):
        message = IrcMessage(command=0)
        with self.assertRaises(AttributeError):
            message.command = IrcMessageTagsReadOnly()

    def test_command_set_params(self):
        message = IrcMessage(command=0)
        with self.assertRaises(AttributeError):
            message.params = IrcMessageParams()

    def test_command(self):
        message = IrcMessage(command='RECONNECT')
        self.assertIsNone(message.tags)
        self.assertIsNone(message.prefix)
        self.assertEqual(message.command, 'RECONNECT')
        self.assertIsNotNone(message.params)
        self.assertIs(message.params.isEmpty, True)
        self.assertEqual(message, IrcMessage(command='RECONNECT'))

    def test_command_params_middle(self):
        message = IrcMessage(command='JOIN',
                             params=IrcMessageParams(middle='#botgotsthis'))
        self.assertIsNone(message.tags)
        self.assertIsNone(message.prefix)
        self.assertEqual(message.command, 'JOIN')
        self.assertIs(message.params.middle, '#botgotsthis')
        self.assertIs(message.params.trailing, None)
        self.assertEqual(message,
                         IrcMessage(command='JOIN',
                                    params=IrcMessageParams('#botgotsthis')))

    def test_command_params_middle_trailing(self):
        message = IrcMessage(command='PRIVMSG',
                             params=IrcMessageParams(middle='#botgotsthis',
                                                     trailing='Hello World'))
        self.assertIsNone(message.tags)
        self.assertIsNone(message.prefix)
        self.assertEqual(message.command, 'PRIVMSG')
        self.assertIs(message.params.middle, '#botgotsthis')
        self.assertIs(message.params.trailing, 'Hello World')
        self.assertEqual(
            message,
            IrcMessage(command='PRIVMSG',
                       params=IrcMessageParams('#botgotsthis', 'Hello World')))

    def test_prefix_command_params(self):
        message = IrcMessage(
            prefix=IrcMessagePrefix(
                nick='botgotsthis',
                user='botgotsthis',
                host='botgotsthis.tmi.twitch.tv'),
            command='PART',
            params=IrcMessageParams('#botgotsthis'))
        self.assertIsNone(message.prefix.servername)
        self.assertEqual(message.prefix.nick, 'botgotsthis')
        self.assertEqual(message.prefix.user, 'botgotsthis')
        self.assertEqual(message.prefix.host, 'botgotsthis.tmi.twitch.tv')
        self.assertEqual(message.command, 'PART')
        self.assertIs(message.params.middle, '#botgotsthis')
        self.assertIs(message.params.trailing, None)
        self.assertEqual(
            message,
            IrcMessage(
                prefix=IrcMessagePrefix(
                    nick='botgotsthis',
                    user='botgotsthis',
                    host='botgotsthis.tmi.twitch.tv'),
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

    def test_str_magic_command(self):
        self.assertEqual(str(IrcMessage(command='RECONNECT')),
                         'RECONNECT')

    def test_str_magic_command_params_middle(self):
        self.assertEqual(
            str(IrcMessage(command='JOIN',
                           params=IrcMessageParams(middle='#botgotsthis'))),
            'JOIN #botgotsthis')

    def test_str_magic_command_params_middle_trailing(self):
        self.assertEqual(
            str(IrcMessage(command='PRIVMSG',
                           params=IrcMessageParams(middle='#botgotsthis',
                                                   trailing='Hello World'))),
            'PRIVMSG #botgotsthis :Hello World')

    def test_str_magic_prefix_command_params(self):
        self.assertEqual(
            str(IrcMessage(
                prefix=IrcMessagePrefix(nick='botgotsthis',
                                        user='botgotsthis',
                                        host='botgotsthis.tmi.twitch.tv'),
                command='PART',
                params=IrcMessageParams('#botgotsthis'))),
            '''\
:botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv PART #botgotsthis''')

    def test_str_tags_magic_prefix_command_params(self):
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
        self.assertEqual(
            str(message),
            '@' + str(message.tags) + ' :tmi.twitch.tv ROOMSTATE #botgotsthis')

    def test_parse_none(self):
        self.assertRaises(TypeError, IrcMessage.parse, None)

    def test_parse_int(self):
        self.assertRaises(TypeError, IrcMessage.parse, 0)

    def test_parse_list(self):
        self.assertRaises(TypeError, IrcMessage.parse, [])

    def test_parse_dict(self):
        self.assertRaises(TypeError, IrcMessage.parse, {})

    def test_parse_bytes(self):
        self.assertRaises(TypeError, IrcMessage.parse, b'')

    def test_parse_empty(self):
        self.assertRaises(ValueError, IrcMessage.parse, '')

    def test_parse_space(self):
        self.assertRaises(ValueError, IrcMessage.parse, ' ')

    def test_parse_leading_space(self):
        self.assertRaises(ValueError, IrcMessage.parse, ' ABC')

    def test_parse_tab(self):
        self.assertRaises(ValueError, IrcMessage.parse, '\t')

    def test_parse_nl(self):
        self.assertRaises(ValueError, IrcMessage.parse, '\n')

    def test_parse_cr(self):
        self.assertRaises(ValueError, IrcMessage.parse, '\r')

    def test_parse_null_char(self):
        self.assertRaises(ValueError, IrcMessage.parse, '\0')

    def test_parse_number_len_1(self):
        self.assertRaises(ValueError, IrcMessage.parse, '1')

    def test_parse_number_len_2(self):
        self.assertRaises(ValueError, IrcMessage.parse, '01')

    def test_parse_number_len_4(self):
        self.assertRaises(ValueError, IrcMessage.parse, '0001')

    def test_parse_number_letter(self):
        self.assertRaises(ValueError, IrcMessage.parse, '0AA')

    def test_parse_number_2_letter(self):
        self.assertRaises(ValueError, IrcMessage.parse, '00A')

    def test_parse_number_3_letter(self):
        self.assertRaises(ValueError, IrcMessage.parse, '000A')

    def test_parse_letter_number(self):
        self.assertRaises(ValueError, IrcMessage.parse, 'A000')

    def test_parse_command_underscore(self):
        self.assertRaises(ValueError, IrcMessage.parse, 'COMMAND_UNDERSCORE')

    def test_parse_only_tags(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@only-tag-here')

    def test_parse_only_tags_trailing_space(self):
        self.assertRaises(ValueError, IrcMessage.parse,
                          '@only-tag-here;with-a-space ')

    def test_parse_only_prefix_servername(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':prefix.only')

    def test_parse_only_prefix_nick_user_host(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':prefix!only@here')

    def test_parse_only_prefix_servername_trailing_space(self):
        self.assertRaises(ValueError, IrcMessage.parse,
                          ':prefix.need.a.space ')

    def test_parse_leading_exclamation(self):
        self.assertRaises(ValueError, IrcMessage.parse,
                          '!invalid starting char')

    def test_parse_leading_number_sign(self):
        self.assertRaises(ValueError, IrcMessage.parse,
                          '#invalid starting char')

    def test_parse_leading_dollar_sign(self):
        self.assertRaises(ValueError, IrcMessage.parse,
                          '$invalid starting char')

    def test_parse_tags_empty(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@ 001')

    def test_parse_tags_null_char(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@\0 001')

    def test_parse_tags_cr(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@\r 001')

    def test_parse_tags_nl(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@\n 001')

    def test_parse_tags_opening_parenthesis(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@( 001')

    def test_parse_tags_closing_parenthesis(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@) 001')

    def test_parse_tags_opening_bracket(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@[ 001')

    def test_parse_tags_closing_bracket(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@] 001')

    def test_parse_tags_key_exclamation(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@a! 001')

    def test_parse_tags_key_ampersand(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@a& 001')

    def test_parse_tags_key_exclamation_empty(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@a!= 001')

    def test_parse_tags_value_nl(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@a=\n 001')

    def test_parse_tags_value_cr(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@a=\r 001')

    def test_parse_tags_value_backslash(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@a=\\ 001')

    def test_parse_tags_value_null_char(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@a=\0 001')

    def test_parse_tags_double_empty_tags(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@; 001')

    def test_parse_tags_trailing_empty_tag(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@a; 001')

    def test_parse_tags_leading_empty_tag(self):
        self.assertRaises(ValueError, IrcMessage.parse, '@;a 001')

    def test_parse_prefix_empty(self):
        self.assertRaises(ValueError, IrcMessage.parse, ': 001')

    def test_parse_prefix_empty_nick_user(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':! 001')

    def test_parse_prefix_user_empty_nick(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':!a 001')

    def test_parse_prefix_nick_empty_user(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':a! 001')

    def test_parse_prefix_empty_nick_host(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':@ 001')

    def test_parse_prefix_nick_empty_host(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':a@ 001')

    def test_parse_prefix_host_empty_nick(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':@a 001')

    def test_parse_prefix_empty_nick_user_host(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':!@ 001')

    def test_parse_prefix_nick_empty_user_host(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':a!@ 001')

    def test_parse_prefix_user_empty_nick_host(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':!a@ 001')

    def test_parse_prefix_host_empty_nick_user(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':!@a 001')

    def test_parse_prefix_nick_user_empty_host(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':a!a@ 001')

    def test_parse_prefix_nick_host_empty_user(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':a!@a 001')

    def test_parse_prefix_user_host_empty_nick(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':!a@a 001')

    def test_parse_prefix_nick_period(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':a.a!a@a 001')

    def test_parse_prefix_user_period(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':a!a.a@a 001')

    def test_parse_prefix_host_trailing_period(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':a!a@a. 001')

    def test_parse_prefix_host_leading_period(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':a!a@.a 001')

    def test_parse_prefix_trailing_period(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':a. 001')

    def test_parse_prefix_leading_period(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':.a 001')

    def test_parse_prefix_opening_parenthesis(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':( 001')

    def test_parse_prefix_leading_parenthesis(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':) 001')

    def test_parse_prefix_opening_bracket(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':[ 001')

    def test_parse_prefix_closing_bracket(self):
        self.assertRaises(ValueError, IrcMessage.parse, ':] 001')

    def test_parse_params_middle_null_char(self):
        self.assertRaises(ValueError, IrcMessage.parse, '001 \0')

    def test_parse_params_middle_cr(self):
        self.assertRaises(ValueError, IrcMessage.parse, '001 \r')

    def test_parse_params_middle_nl(self):
        self.assertRaises(ValueError, IrcMessage.parse, '001 \n')

    def test_parse_params_trailing_null_char(self):
        self.assertRaises(ValueError, IrcMessage.parse, '001 :\0')

    def test_parse_params_trailing_cr(self):
        self.assertRaises(ValueError, IrcMessage.parse, '001 :\r')

    def test_parse_params_trailing_nl(self):
        self.assertRaises(ValueError, IrcMessage.parse, '001 :\n')

    def test_parse_command(self):
        self.assertEqual(IrcMessage.parse('RECONNECT'),
                         ParsedMessage(None, None, 'RECONNECT',
                                       IrcMessageParams()))

    def test_parse_command_int(self):
        self.assertEqual(IrcMessage.parse('001'),
                         ParsedMessage(None, None, 1, IrcMessageParams()))

    def test_parse_command_params_middle(self):
        self.assertEqual(IrcMessage.parse('PART #botgotsthis'),
                         ParsedMessage(None, None, 'PART',
                                       IrcMessageParams('#botgotsthis')))

    def test_parse_prefix_command_params_middle(self):
        self.assertEqual(
            IrcMessage.parse('''\
:bot_gots_this!123botgotsthis@botgotsthis.tmi.twitch.tv JOIN #botgotsthis'''),
            ParsedMessage(None,
                          IrcMessagePrefix(nick='bot_gots_this',
                                           user='123botgotsthis',
                                           host='botgotsthis.tmi.twitch.tv'),
                          'JOIN',
                          IrcMessageParams('#botgotsthis')))

    def test_parse_prefix_servername_command_params_middle_trailing(self):
        self.assertEqual(
            IrcMessage.parse(':tmi.twitch.tv PONG tmi.twitch.tv :botgotsthis'),
            ParsedMessage(None,
                          IrcMessagePrefix(servername='tmi.twitch.tv'),
                          'PONG',
                          IrcMessageParams('tmi.twitch.tv', 'botgotsthis')))

    def test_parse_empty_trailing(self):
        self.assertEqual(
            IrcMessage.parse('TEST middle empty trail :'),
            ParsedMessage(None, None, 'TEST',
                          IrcMessageParams('middle empty trail', '')))

    def test_parse_empty_middle(self):
        self.assertEqual(IrcMessage.parse('TEST :empty middle'),
                         ParsedMessage(None, None, 'TEST',
                                       IrcMessageParams(None, 'empty middle')))

    def test_parse_multiple_spaces(self):
        self.assertEqual(
            IrcMessage.parse('''\
@multiple=spaces  :will!be@used  HERE  to  test :if  this  passes'''),
            ParsedMessage(
                IrcMessageTagsReadOnly({'multiple': 'spaces'}),
                IrcMessagePrefix(nick='will', user='be', host='used'),
                'HERE', IrcMessageParams('to test', 'if  this  passes')))

    def test_from_command(self):
        self.assertEqual(IrcMessage.fromMessage('RECONNECT'),
                         IrcMessage(command='RECONNECT'))

    def test_from_command_param_middle(self):
        self.assertEqual(IrcMessage.fromMessage('PART #botgotsthis'),
                         IrcMessage(command='PART',
                                    params=IrcMessageParams(
                                        middle='#botgotsthis')))

    def test_from_prefix_command_param_middle(self):
        self.assertEqual(
            IrcMessage.fromMessage('''\
:botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv JOIN #botgotsthis'''),
            IrcMessage(
                prefix=IrcMessagePrefix(nick='botgotsthis',
                                        user='botgotsthis',
                                        host='botgotsthis.tmi.twitch.tv'),
                command='JOIN',
                params=IrcMessageParams(middle='#botgotsthis')))

    def test_from_twitch_privmsg(self):
        self.assertEqual(
            IrcMessage.fromMessage(
                '@badges=broadcaster/1;color=#DAA520;display-name=BotGotsThis;'
                'emotes=25:6-10;mod=1;room-id=42553092;subscriber=0;turbo=0;'
                'user-id=55612319;user-type=mod '
                ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv '
                'PRIVMSG #botgotsthis :Hello Kappa'),
            IrcMessage(
                tags=IrcMessageTagsReadOnly({
                    'badges': 'broadcaster/1',
                    'color': '#DAA520',
                    'display-name': 'BotGotsThis',
                    'emotes': '25:6-10',
                    'mod': '1',
                    'room-id': '42553092',
                    'subscriber': '0',
                    'turbo': '0',
                    'user-id': '55612319',
                    'user-type': 'mod'
                }),
                prefix=IrcMessagePrefix(nick='botgotsthis',
                                        user='botgotsthis',
                                        host='botgotsthis.tmi.twitch.tv'),
                command='PRIVMSG',
                params=IrcMessageParams(middle='#botgotsthis',
                                        trailing='Hello Kappa')))

    def test_from_twitch_001(self):
        self.assertEqual(
            IrcMessage.fromMessage(
                ':tmi.twitch.tv 001 botgotsthis :Welcome, GLHF!'),
            IrcMessage(prefix=IrcMessagePrefix(servername='tmi.twitch.tv'),
                       command=1,
                       params=IrcMessageParams(middle='botgotsthis',
                                               trailing='Welcome, GLHF!')))

    def test_from_twitch_privmsg_bits(self):
        IrcMessage.fromMessage('''\
@badges=staff/1,bits/1000;bits=100;color=;display-name=TWITCH_UserNaME;\
emotes=;id=b34ccfc7-4977-403a-8a94-33c6bac34fb8;mod=0;room-id=1337;\
subscriber=0;turbo=1;user-id=1337;user-type=staff \
:twitch_username!twitch_username@twitch_username.tmi.twitch.tv \
PRIVMSG #channel :cheer100''')
