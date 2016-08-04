import unittest
from bot.twitchmessage import IrcMessageParams
from bot.twitchmessage._ircparams import ParsedParams


class TestsIrcParams(unittest.TestCase):
    def test_constructor_middle_int(self):
        self.assertRaises(TypeError, IrcMessageParams, middle=1)

    def test_constructor_trailing_int(self):
        self.assertRaises(TypeError, IrcMessageParams, trailing=1)

    def test_constructor_middle_bytes(self):
        self.assertRaises(TypeError, IrcMessageParams, middle=b'')

    def test_constructor_trailing_bytes(self):
        self.assertRaises(TypeError, IrcMessageParams, trailing=b'')

    def test_constructor_middle_list(self):
        self.assertRaises(TypeError, IrcMessageParams, middle=[])

    def test_constructor_trailing_list(self):
        self.assertRaises(TypeError, IrcMessageParams, trailing=[])

    def test_constructor_middle_starting_colon(self):
        self.assertRaises(ValueError, IrcMessageParams, middle=':a')

    def test_constructor_middle_second_starting_colon(self):
        self.assertRaises(ValueError, IrcMessageParams, middle='a :b')

    def test_constructor_middle_null_char(self):
        self.assertRaises(ValueError, IrcMessageParams, middle='\0')

    def test_constructor_middle_cr(self):
        self.assertRaises(ValueError, IrcMessageParams, middle='\r')

    def test_constructor_middle_nl(self):
        self.assertRaises(ValueError, IrcMessageParams, middle='\n')

    def test_constructor_trailing_null_char(self):
        self.assertRaises(ValueError, IrcMessageParams, trailing='\0')

    def test_constructor_trailing_cr(self):
        self.assertRaises(ValueError, IrcMessageParams, trailing='\r')

    def test_constructor_trailing_nl(self):
        self.assertRaises(ValueError, IrcMessageParams, trailing='\n')

    def test_constructor_middle_empty(self):
        self.assertRaises(ValueError, IrcMessageParams, middle='')

    def test_constructor_middle_space(self):
        self.assertRaises(ValueError, IrcMessageParams, middle=' ')

    def test_constructor_middle_spaces(self):
        self.assertRaises(ValueError, IrcMessageParams, middle='  ')

    def test_empty(self):
        params = IrcMessageParams()
        self.assertIsNone(params.middle)
        self.assertIsNone(params.trailing)
        self.assertEqual(params, IrcMessageParams())
        self.assertIs(params.isEmpty, True)

    def test_set_middle(self):
        params = IrcMessageParams()
        with self.assertRaises(AttributeError):
            params.middle = ''

    def test_set_trailing(self):
        params = IrcMessageParams()
        with self.assertRaises(AttributeError):
            params.trailing = ''

    def test_middle_one_param(self):
        params = IrcMessageParams(middle='Kappa')
        self.assertEqual(params.middle, 'Kappa')
        self.assertIsNone(params.trailing)
        self.assertEqual(params, IrcMessageParams('Kappa'))
        self.assertIs(params.isEmpty, False)

    def test_middle_two_params(self):
        params = IrcMessageParams(middle='Kappa Keepo')
        self.assertEqual(params.middle, 'Kappa Keepo')
        self.assertEqual(params, IrcMessageParams('Kappa Keepo'))

    def test_trailing_empty(self):
        params = IrcMessageParams(trailing='')
        self.assertIsNone(params.middle)
        self.assertEqual(params.trailing, '')
        self.assertEqual(params, IrcMessageParams(None, ''))
        self.assertIs(params.isEmpty, False)

    def test_trailing(self):
        params = IrcMessageParams(trailing='Kappa')
        self.assertEqual(params.trailing, 'Kappa')
        self.assertEqual(params, IrcMessageParams(None, 'Kappa'))

    def test_trailing_starting_colon(self):
        params = IrcMessageParams(trailing=':Kappa')
        self.assertEqual(params.trailing, ':Kappa')

    def test_trailing_starting_space(self):
        params = IrcMessageParams(trailing=' Kappa')
        self.assertEqual(params.trailing, ' Kappa')

    def test_trailing_complex(self):
        params = IrcMessageParams(trailing='Kappa Keepo :KappaPride')
        self.assertEqual(params.trailing, 'Kappa Keepo :KappaPride')

    def test_middle_trailing(self):
        params = IrcMessageParams(middle='Kappa Kappa', trailing='Kappa')
        self.assertEqual(params.middle, 'Kappa Kappa')
        self.assertEqual(params.trailing, 'Kappa')
        self.assertEqual(params, IrcMessageParams('Kappa Kappa', 'Kappa'))
        self.assertIs(params.isEmpty, False)

    def test_middle_trailing_2(self):
        params = IrcMessageParams(middle='Kappa Kappa', trailing=':Kappa Kappa')
        self.assertEqual(params.middle, 'Kappa Kappa')
        self.assertEqual(params.trailing, ':Kappa Kappa')

    def test_str_magic_empty(self):
        self.assertEqual(str(IrcMessageParams()), '')

    def test_str_magic_middle_one_param(self):
        self.assertEqual(str(IrcMessageParams(middle='Kappa')), 'Kappa')

    def test_str_magic_middle_two_params(self):
        self.assertEqual(str(IrcMessageParams(middle='Kappa Keepo')),
                         'Kappa Keepo')

    def test_str_magic_trailing_empty(self):
        self.assertEqual(str(IrcMessageParams(trailing='')), ':')

    def test_str_magic_trailing(self):
        self.assertEqual(str(IrcMessageParams(trailing='Kappa')), ':Kappa')

    def test_str_magic_trailing_starting_colon(self):
        self.assertEqual(str(IrcMessageParams(trailing=':Kappa')), '::Kappa')

    def test_str_magic_trailing_starting_space(self):
        self.assertEqual(str(IrcMessageParams(trailing=' Kappa')), ': Kappa')

    def test_str_magic_trailing_complex(self):
        self.assertEqual(str(IrcMessageParams(trailing='Kappa Keepo :KappaPride')),
                         ':Kappa Keepo :KappaPride')

    def test_str_magic_middle_trailing(self):
        self.assertEqual(str(IrcMessageParams(middle='Kappa Kappa', trailing='Kappa')),
                         'Kappa Kappa :Kappa')

    def test_from_empty(self):
        self.assertEqual(IrcMessageParams.fromParams(''), IrcMessageParams())

    def test_from_middle(self):
        self.assertEqual(IrcMessageParams.fromParams('Kappa'),
                         IrcMessageParams(middle='Kappa'))

    def test_from_trailing(self):
        self.assertEqual(IrcMessageParams.fromParams(':Kappa'),
                         IrcMessageParams(trailing='Kappa'))

    def test_from_middle_trailing(self):
        self.assertEqual(IrcMessageParams.fromParams('Kappa :KappaPride'),
                         IrcMessageParams(middle='Kappa', trailing='KappaPride'))

    def test_from_channel(self):
        self.assertEqual(IrcMessageParams.fromParams('#botgotsthis'),
                         IrcMessageParams(middle='#botgotsthis'))

    def test_from_list_who(self):
        self.assertEqual(IrcMessageParams.fromParams('botgotsthis = #botgotsthis :megotsthis botgotsthis'),
                         IrcMessageParams(middle='botgotsthis = #botgotsthis', trailing='megotsthis botgotsthis'))

    def test_parse_none(self):
        self.assertRaises(TypeError, IrcMessageParams.parse, None)

    def test_parse_int(self):
        self.assertRaises(TypeError, IrcMessageParams.parse, 1)

    def test_parse_bytes(self):
        self.assertRaises(TypeError, IrcMessageParams.parse, b'')

    def test_parse_list(self):
        self.assertRaises(TypeError, IrcMessageParams.parse, [])

    def test_parse_empty(self):
        self.assertEqual(IrcMessageParams.parse(''), ParsedParams(None, None))

    def test_parse_middle_single(self):
        self.assertEqual(IrcMessageParams.parse('Kappa'),
                         ParsedParams('Kappa', None))

    def test_parse_trailing_empty(self):
        self.assertEqual(IrcMessageParams.parse(':'),
                         ParsedParams(None, ''))

    def test_parse_middle_space_trailing_empty(self):
        self.assertEqual(IrcMessageParams.parse(' :'),
                         ParsedParams(None, ''))

    def test_parse_trailing(self):
        self.assertEqual(IrcMessageParams.parse(':Kappa'),
                         ParsedParams(None, 'Kappa'))

    def test_parse_trailing_leading_colon(self):
        self.assertEqual(IrcMessageParams.parse('::Kappa'),
                         ParsedParams(None, ':Kappa'))

    def test_parse_trailing_leading_space(self):
        self.assertEqual(IrcMessageParams.parse(': Kappa'),
                         ParsedParams(None, ' Kappa'))

    def test_parse_middle_trailing_empty(self):
        self.assertEqual(IrcMessageParams.parse('Kappa :'),
                         ParsedParams('Kappa', ''))

    def test_parse_middle_trailing(self):
        self.assertEqual(IrcMessageParams.parse('Kappa :KappaPride'),
                         ParsedParams('Kappa', 'KappaPride'))

    def test_parse_channel(self):
        self.assertEqual(IrcMessageParams.parse('#botgotsthis'),
                         ParsedParams('#botgotsthis', None))

    def test_parse_list_who(self):
        self.assertEqual(IrcMessageParams.parse('botgotsthis = #botgotsthis :megotsthis botgotsthis'),
                         ParsedParams('botgotsthis = #botgotsthis', 'megotsthis botgotsthis'))
