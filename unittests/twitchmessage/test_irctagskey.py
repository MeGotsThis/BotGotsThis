import unittest
from collections.abc import Hashable
from bot.twitchmessage import IrcMessageTagsKey
from bot.twitchmessage._irctags import ParsedKeyVendor


class TestsIrcTagsKey(unittest.TestCase):
    def test_constructor(self):
        key = IrcMessageTagsKey()
        self.assertEqual(key.vendor, None)
        self.assertEqual(key.key, '')

        key = IrcMessageTagsKey('Kappa')
        self.assertEqual(key.vendor, None)
        self.assertEqual(key.key, 'Kappa')

        self.assertRaises(TypeError, IrcMessageTagsKey, None)
        self.assertRaises(TypeError, IrcMessageTagsKey, b'Kappa')
        self.assertRaises(TypeError, IrcMessageTagsKey, 123)
        self.assertRaises(TypeError, IrcMessageTagsKey, b'Kappa', None)
        self.assertRaises(TypeError, IrcMessageTagsKey, b'Kappa', 'Keepo')
        self.assertRaises(TypeError, IrcMessageTagsKey, 'Kappa', b'Keepo')

        key = IrcMessageTagsKey('Kappa', None)
        self.assertEqual(key.vendor, None)
        self.assertEqual(key.key, 'Kappa')

        key = IrcMessageTagsKey('Kappa', 'Keepo')
        self.assertEqual(key.vendor, 'Keepo')
        self.assertEqual(key.key, 'Kappa')

    def test_magic_str(self):
        key = IrcMessageTagsKey()
        self.assertEqual(str(key), '')

        key = IrcMessageTagsKey('Kappa')
        self.assertEqual(str(key), 'Kappa')

        key = IrcMessageTagsKey('Kappa', 'Keepo')
        self.assertEqual(str(key), 'Keepo/Kappa')

        key = IrcMessageTagsKey('', 'Keepo')
        self.assertEqual(str(key), 'Keepo/')

    def test_from_str(self):
        self.assertRaises(TypeError, IrcMessageTagsKey.fromKeyVendor, b'a')
        self.assertRaises(TypeError, IrcMessageTagsKey.fromKeyVendor, 1)

        key = IrcMessageTagsKey.fromKeyVendor('')
        self.assertEqual(key.vendor, None)
        self.assertEqual(key.key, '')

        key = IrcMessageTagsKey.fromKeyVendor('DansGame')
        self.assertEqual(key.vendor, None)
        self.assertEqual(key.key, 'DansGame')

        key = IrcMessageTagsKey.fromKeyVendor('123')
        self.assertEqual(key.vendor, None)
        self.assertEqual(key.key, '123')

        key = IrcMessageTagsKey.fromKeyVendor('DansGame/')
        self.assertEqual(key.vendor, 'DansGame')
        self.assertEqual(key.key, '')

        key = IrcMessageTagsKey.fromKeyVendor('DansGame/SwiftRage')
        self.assertEqual(key.vendor, 'DansGame')
        self.assertEqual(key.key, 'SwiftRage')

        key = IrcMessageTagsKey.fromKeyVendor('DansGame.com/SwiftRage')
        self.assertEqual(key.vendor, 'DansGame.com')
        self.assertEqual(key.key, 'SwiftRage')

        self.assertRaises(ValueError, IrcMessageTagsKey.fromKeyVendor, '!')
        self.assertRaises(ValueError, IrcMessageTagsKey.fromKeyVendor, '@')
        self.assertRaises(ValueError, IrcMessageTagsKey.fromKeyVendor, '#')
        self.assertRaises(ValueError, IrcMessageTagsKey.fromKeyVendor, '/')
        self.assertRaises(ValueError, IrcMessageTagsKey.fromKeyVendor, '1/')
        self.assertRaises(ValueError, IrcMessageTagsKey.fromKeyVendor, 'abc.cd./abc')
        self.assertRaises(ValueError, IrcMessageTagsKey.fromKeyVendor, 'abc.d')
        self.assertRaises(ValueError, IrcMessageTagsKey.fromKeyVendor, '/abc')
        self.assertRaises(ValueError, IrcMessageTagsKey.fromKeyVendor, ' ')
        self.assertRaises(ValueError, IrcMessageTagsKey.fromKeyVendor, 'a ')
        self.assertRaises(ValueError, IrcMessageTagsKey.fromKeyVendor, ' a')
        self.assertRaises(ValueError, IrcMessageTagsKey.fromKeyVendor, ' a ')

    def test_equals(self):
        self.assertEqual(IrcMessageTagsKey.fromKeyVendor('OpieOP.SoBayed/PJSalt'),
                         IrcMessageTagsKey('PJSalt', 'OpieOP.SoBayed'))
        self.assertNotEqual(IrcMessageTagsKey.fromKeyVendor('abc'),
                            IrcMessageTagsKey('123'))

    def test_hash(self):
        key = IrcMessageTagsKey()
        self.assertIsInstance(hash(key), int)
        self.assertIsInstance(key, Hashable)

    def test_parse(self):
        self.assertEquals(IrcMessageTagsKey.parse(''), ParsedKeyVendor('', None))
        self.assertEquals(IrcMessageTagsKey.parse('Kreygasm'),
                          ParsedKeyVendor('Kreygasm', None))
        self.assertEquals(IrcMessageTagsKey.parse('PogChamp/Kreygasm'),
                          ParsedKeyVendor('Kreygasm', 'PogChamp'))
        self.assertEquals(IrcMessageTagsKey.parse('PogChamp/Kreygasm'),
                          ParsedKeyVendor('Kreygasm', 'PogChamp'))

        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '!')
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '@')
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '#')
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '/')
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '/a')
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, ' ')
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, 'a ')
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, ' a')
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, ' a ')
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '.')
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, 'a.')
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '.a')
