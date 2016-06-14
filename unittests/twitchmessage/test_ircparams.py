import unittest
from bot.twitchmessage import IrcMessageParams
from bot.twitchmessage._ircparams import ParsedParams


class TestsIrcParams(unittest.TestCase):
    def test_excepts(self):
        self.assertRaises(TypeError, IrcMessageParams, 1)
        self.assertRaises(TypeError, IrcMessageParams, None, 1)
        self.assertRaises(TypeError, IrcMessageParams, b'')
        self.assertRaises(TypeError, IrcMessageParams, None, b'')
        self.assertRaises(TypeError, IrcMessageParams, [])
        self.assertRaises(TypeError, IrcMessageParams, None, [])
        self.assertRaises(ValueError, IrcMessageParams, ':a')
        self.assertRaises(ValueError, IrcMessageParams, 'a :b')
        self.assertRaises(ValueError, IrcMessageParams, '\0')
        self.assertRaises(ValueError, IrcMessageParams, '\r')
        self.assertRaises(ValueError, IrcMessageParams, '\n')
        self.assertRaises(ValueError, IrcMessageParams, None, '\0')
        self.assertRaises(ValueError, IrcMessageParams, None, '\r')
        self.assertRaises(ValueError, IrcMessageParams, None, '\n')
        self.assertRaises(ValueError, IrcMessageParams, '', None)
        self.assertRaises(ValueError, IrcMessageParams, ' ', None)
        self.assertRaises(ValueError, IrcMessageParams, '  ', None)

    def test_empty(self):
        params = IrcMessageParams()
        self.assertIsNone(params.middle)
        self.assertIsNone(params.trailing)
        self.assertEqual(str(params), '')
        self.assertEqual(params, IrcMessageParams())
        self.assertIs(params.isEmpty, True)
        with self.assertRaises(AttributeError):
            params.middle = ''
        with self.assertRaises(AttributeError):
            params.trailing = ''

    def test_middle(self):
        params = IrcMessageParams('Kappa')
        self.assertEqual(params.middle, 'Kappa')
        self.assertIsNone(params.trailing)
        self.assertEqual(str(params), 'Kappa')
        self.assertEqual(params, IrcMessageParams('Kappa'))
        self.assertIs(params.isEmpty, False)

        params = IrcMessageParams('Kappa Keepo')
        self.assertEqual(params.middle, 'Kappa Keepo')
        self.assertIsNone(params.trailing)
        self.assertEqual(str(params), 'Kappa Keepo')
        self.assertEqual(params, IrcMessageParams('Kappa Keepo'))
        self.assertIs(params.isEmpty, False)

    def test_trailing(self):
        params = IrcMessageParams(None, 'Kappa')
        self.assertIsNone(params.middle)
        self.assertEqual(params.trailing, 'Kappa')
        self.assertEqual(str(params), ':Kappa')
        self.assertEqual(params, IrcMessageParams(None, 'Kappa'))
        self.assertIs(params.isEmpty, False)

        params = IrcMessageParams(None, ':Kappa')
        self.assertIsNone(params.middle)
        self.assertEqual(params.trailing, ':Kappa')
        self.assertEqual(str(params), '::Kappa')

        params = IrcMessageParams(None, ' Kappa')
        self.assertIsNone(params.middle)
        self.assertEqual(params.trailing, ' Kappa')
        self.assertEqual(str(params), ': Kappa')

        params = IrcMessageParams(None, 'Kappa Keepo :KappaPride')
        self.assertIsNone(params.middle)
        self.assertEqual(params.trailing, 'Kappa Keepo :KappaPride')
        self.assertEqual(str(params), ':Kappa Keepo :KappaPride')

    def test_middle_trailing(self):
        params = IrcMessageParams('Kappa Kappa', 'Kappa')
        self.assertEqual(params.middle, 'Kappa Kappa')
        self.assertEqual(params.trailing, 'Kappa')
        self.assertEqual(str(params), 'Kappa Kappa :Kappa')
        self.assertEqual(params, IrcMessageParams('Kappa Kappa', 'Kappa'))
        self.assertIs(params.isEmpty, False)

        params = IrcMessageParams('Kappa Kappa', ':Kappa Kappa')
        self.assertEqual(params.middle, 'Kappa Kappa')
        self.assertEqual(params.trailing, ':Kappa Kappa')
        self.assertEqual(str(params), 'Kappa Kappa ::Kappa Kappa')

    def test_from(self):
        self.assertRaises(TypeError, IrcMessageParams.fromParams, None)
        self.assertRaises(TypeError, IrcMessageParams.fromParams, 1)
        self.assertRaises(TypeError, IrcMessageParams.fromParams, b'')
        self.assertRaises(TypeError, IrcMessageParams.fromParams, [])

        params = IrcMessageParams.fromParams('')
        self.assertIsNone(params.middle)
        self.assertIsNone(params.trailing)
        self.assertEqual(params, IrcMessageParams())

        params = IrcMessageParams.fromParams('Kappa')
        self.assertEqual(params.middle, 'Kappa')
        self.assertIsNone(params.trailing)
        self.assertEqual(params, IrcMessageParams('Kappa'))

        params = IrcMessageParams.fromParams(':Kappa')
        self.assertIsNone(params.middle)
        self.assertEqual(params.trailing, 'Kappa')
        self.assertEqual(params, IrcMessageParams(None, 'Kappa'))

        self.assertEqual(IrcMessageParams.fromParams('::Kappa'),
                         IrcMessageParams(None, ':Kappa'))

        self.assertEqual(IrcMessageParams.fromParams(': Kappa'),
                         IrcMessageParams(None, ' Kappa'))

        params = IrcMessageParams.fromParams('Kappa :KappaPride')
        self.assertEqual(params.middle, 'Kappa')
        self.assertEqual(params.trailing, 'KappaPride')
        self.assertEqual(params, IrcMessageParams('Kappa', 'KappaPride'))

        self.assertEqual(IrcMessageParams.fromParams('#botgotsthis'),
                         IrcMessageParams('#botgotsthis'))

        self.assertEqual(IrcMessageParams.fromParams('botgotsthis = #botgotsthis :megotsthis botgotsthis'),
                         IrcMessageParams('botgotsthis = #botgotsthis', 'megotsthis botgotsthis'))

    def test_parse(self):
        self.assertRaises(TypeError, IrcMessageParams.parse, None)
        self.assertRaises(TypeError, IrcMessageParams.parse, 1)
        self.assertRaises(TypeError, IrcMessageParams.parse, b'')
        self.assertRaises(TypeError, IrcMessageParams.parse, [])

        self.assertEqual(IrcMessageParams.parse(''), ParsedParams(None, None))
        self.assertEqual(IrcMessageParams.parse('Kappa'),
                         ParsedParams('Kappa', None))
        self.assertEqual(IrcMessageParams.parse(':Kappa'),
                         ParsedParams(None, 'Kappa'))
        self.assertEqual(IrcMessageParams.parse('::Kappa'),
                         ParsedParams(None, ':Kappa'))
        self.assertEqual(IrcMessageParams.parse(': Kappa'),
                         ParsedParams(None, ' Kappa'))
        self.assertEqual(IrcMessageParams.parse('Kappa :KappaPride'),
                         ParsedParams('Kappa', 'KappaPride'))
        self.assertEqual(IrcMessageParams.parse('#botgotsthis'),
                         ParsedParams('#botgotsthis', None))
        self.assertEqual(IrcMessageParams.parse('botgotsthis = #botgotsthis :megotsthis botgotsthis'),
                         ParsedParams('botgotsthis = #botgotsthis', 'megotsthis botgotsthis'))
