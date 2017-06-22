import unittest
from collections.abc import Hashable as HashableAbc
from typing import Hashable
from bot.twitchmessage import IrcMessageTagsKey
from bot.twitchmessage._irctags import ParsedKeyVendor


class TestsIrcTagsKey(unittest.TestCase):
    def test_empty_constructor(self):
        key = IrcMessageTagsKey()
        self.assertEqual(key.vendor, None)
        self.assertEqual(key.key, '')

    def test_constructor_key(self):
        key = IrcMessageTagsKey(key='Kappa')
        self.assertEqual(key.vendor, None)
        self.assertEqual(key.key, 'Kappa')

    def test_constructor_key_None(self):
        self.assertRaises(TypeError, IrcMessageTagsKey, key=None)

    def test_constructor_key_bytes(self):
        self.assertRaises(TypeError, IrcMessageTagsKey, key=b'Kappa')

    def test_constructor_key_int(self):
        self.assertRaises(TypeError, IrcMessageTagsKey, key=123)

    def test_constructor_key_bytes_vendor_None(self):
        self.assertRaises(TypeError, IrcMessageTagsKey, vendor=None, key=b'Kappa')

    def test_constructor_key_bytes_vendor(self):
        self.assertRaises(TypeError, IrcMessageTagsKey, vendor='Keepo', key=b'Kappa')

    def test_constructor_key_vendor_bytes(self):
        self.assertRaises(TypeError, IrcMessageTagsKey, vendor=b'Keepo', key='Kappa')

    def test_constructor_key_vendor_None(self):
        key = IrcMessageTagsKey('Kappa', None)
        self.assertEqual(key.vendor, None)
        self.assertEqual(key.key, 'Kappa')

    def test_constructor_key_vendor(self):
        key = IrcMessageTagsKey('Kappa', 'Keepo')
        self.assertEqual(key.vendor, 'Keepo')
        self.assertEqual(key.key, 'Kappa')

    def test_constructor_vendor(self):
        key = IrcMessageTagsKey(vendor='Kappa')
        self.assertEqual(key.vendor, 'Kappa')
        self.assertEqual(key.key, '')

    def test_constructor_keywords(self):
        key = IrcMessageTagsKey(vendor='Keepo', key='Kappa')
        self.assertEqual(key.vendor, 'Keepo')
        self.assertEqual(key.key, 'Kappa')

    def test_magic_str_empty(self):
        key = IrcMessageTagsKey()
        self.assertEqual(str(key), '')

    def test_magic_str_key(self):
        key = IrcMessageTagsKey(key='Kappa')
        self.assertEqual(str(key), 'Kappa')

    def test_magic_str_key_vendor(self):
        key = IrcMessageTagsKey(vendor='Keepo', key='Kappa')
        self.assertEqual(str(key), 'Keepo/Kappa')

    def test_magic_str_vendor(self):
        key = IrcMessageTagsKey(vendor='Keepo')
        self.assertEqual(str(key), 'Keepo/')

    def test_from_str_bytes(self):
        self.assertRaises(TypeError, IrcMessageTagsKey.fromKeyVendor, b'')

    def test_from_str_integer(self):
        self.assertRaises(TypeError, IrcMessageTagsKey.fromKeyVendor, 1)

    def test_from_str_empty(self):
        key = IrcMessageTagsKey.fromKeyVendor('')
        self.assertEqual(key.vendor, None)
        self.assertEqual(key.key, '')

    def test_from_str_key(self):
        key = IrcMessageTagsKey.fromKeyVendor('DansGame')
        self.assertEqual(key.vendor, None)
        self.assertEqual(key.key, 'DansGame')

    def test_from_str_key_numbers(self):
        key = IrcMessageTagsKey.fromKeyVendor('123')
        self.assertEqual(key.vendor, None)
        self.assertEqual(key.key, '123')

    def test_equals_key(self):
        self.assertEqual(IrcMessageTagsKey.fromKeyVendor('abc'),
                         IrcMessageTagsKey(key='abc'))

    def test_equals_key_vendor(self):
        self.assertEqual(IrcMessageTagsKey.fromKeyVendor('OpieOP.SoBayed/PJSalt'),
                         IrcMessageTagsKey(vendor='OpieOP.SoBayed', key='PJSalt'))

    def test_not_equals_key(self):
        self.assertNotEqual(IrcMessageTagsKey.fromKeyVendor('abc'),
                            IrcMessageTagsKey(key='123'))

    def test_not_equals_key_vendor_by_key(self):
        self.assertNotEqual(IrcMessageTagsKey.fromKeyVendor('OpieOP.SoBayed/PJSalt'),
                            IrcMessageTagsKey(vendor='OpieOP.SoBayed', key='DansGame'))

    def test_not_equals_key_vendor_by_vendor(self):
        self.assertNotEqual(IrcMessageTagsKey.fromKeyVendor('OpieOP.SoBayed/PJSalt'),
                            IrcMessageTagsKey(vendor='SoBayed.OpieOP', key='PJSalt'))

    def test_not_equals_key_vendor(self):
        self.assertNotEqual(IrcMessageTagsKey.fromKeyVendor('OpieOP.SoBayed/PJSalt'),
                            IrcMessageTagsKey(vendor='SoBayed.PJSalt', key='OpieOP'))

    def test_hash(self):
        key = IrcMessageTagsKey()
        self.assertIsInstance(hash(key), int)
        self.assertIsInstance(key, HashableAbc)
        self.assertIsInstance(key, Hashable)

    def test_parse_symbol_exclamation(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '!')

    def test_parse_symbol_at(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '@')

    def test_parse_symbol_number_sign(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '#')

    def test_parse_forward_slash(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '/')

    def test_parse_number_vendor(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '1/')

    def test_parse_empty_vendor(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '/abc')

    def test_parse_space(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, ' ')

    def test_parse_trailing_space(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, 'a ')

    def test_parse_leading_space(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, ' a')

    def test_parse_covering_space(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, ' a ')

    def test_parse_middle_space(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, 'a b')

    def test_parse_period(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '.')

    def test_parse_key_leading_period(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '.a')

    def test_parse_key_trailing_period(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, 'a.')

    def test_parse_key_covering_period(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '.a.')

    def test_parse_key_containing_period(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, 'a.b')

    def test_parse_vendor_period(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, './')

    def test_parse_vendor_leading_period(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '.a/')

    def test_parse_vendor_trailing_period(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, 'a./')

    def test_parse_vendor_surrounding_period(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '.a./')

    def test_parse_vendor_multiple_leading_period(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '.a.a/')

    def test_parse_vendor_multiple_trailing_period(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, 'a.a./')

    def test_parse_vendor_multiple_convering_period(self):
        self.assertRaises(ValueError, IrcMessageTagsKey.parse, '.a.a./')

    def test_parse(self):
        self.assertEqual(IrcMessageTagsKey.parse(''), ParsedKeyVendor('', None))

    def test_parse_key(self):
        self.assertEqual(IrcMessageTagsKey.parse('Kreygasm'),
                         ParsedKeyVendor('Kreygasm', None))

    def test_parse_key_vendor(self):
        self.assertEqual(IrcMessageTagsKey.parse('PogChamp/Kreygasm'),
                         ParsedKeyVendor('Kreygasm', 'PogChamp'))

    def test_parse_key_venor_domain(self):
        self.assertEqual(IrcMessageTagsKey.parse('PogChamp/Kreygasm'),
                         ParsedKeyVendor('Kreygasm', 'PogChamp'))

    def test_from_str_vendor(self):
        key = IrcMessageTagsKey.fromKeyVendor('DansGame/')
        self.assertEqual(key.vendor, 'DansGame')
        self.assertEqual(key.key, '')

    def test_from_str_key_vendor(self):
        key = IrcMessageTagsKey.fromKeyVendor('DansGame/SwiftRage')
        self.assertEqual(key.vendor, 'DansGame')
        self.assertEqual(key.key, 'SwiftRage')

    def test_from_str_key_vendor_domain(self):
        key = IrcMessageTagsKey.fromKeyVendor('DansGame.com/SwiftRage')
        self.assertEqual(key.vendor, 'DansGame.com')
        self.assertEqual(key.key, 'SwiftRage')
