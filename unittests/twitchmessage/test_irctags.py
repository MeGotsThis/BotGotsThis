import unittest
from typing import Dict
from bot.twitchmessage import IrcMessageTags, IrcMessageTagsKey
from bot.twitchmessage import IrcMessageTagsReadOnly
from bot.twitchmessage._irctags import TagValue


class TestsIrcTagsReadOnly(unittest.TestCase):
    def test_fromkey_none(self):
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.fromKey, None)

    def test_fromkey_int(self):
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.fromKey, 1)

    def test_fromkey_bytes(self):
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.fromKey, b'')

    def test_fromkey_str_empty(self):
        key = IrcMessageTagsReadOnly.fromKey('')
        self.assertIsInstance(key, IrcMessageTagsKey)
        self.assertEqual(key, IrcMessageTagsKey())
        self.assertEqual(key, '')

    def test_fromkey_str_key(self):
        key = IrcMessageTagsReadOnly.fromKey('Kappa')
        self.assertEqual(key, IrcMessageTagsKey('Kappa'))
        self.assertEqual(key, 'Kappa')

    def test_fromkey_str_vendor(self):
        key = IrcMessageTagsReadOnly.fromKey('Kappa/Keepo')
        self.assertEqual(key, IrcMessageTagsKey('Keepo', 'Kappa'))
        self.assertEqual(key, 'Kappa/Keepo')

    def test_fromkey_key(self):
        key = IrcMessageTagsKey()
        self.assertIs(IrcMessageTagsReadOnly.fromKey(key), key)

    def test_constructor_int(self):
        self.assertRaises(TypeError, IrcMessageTagsReadOnly, 1)

    def test_constructor_tagkey(self):
        self.assertRaises(TypeError, IrcMessageTagsReadOnly, IrcMessageTagsKey())

    def test_constructor_readonly(self):
        tags = IrcMessageTagsReadOnly()
        self.assertIs(tags, IrcMessageTagsReadOnly(tags))

    def test_empty_instance(self):
        tags = IrcMessageTagsReadOnly()
        self.assertEqual(len(tags), 0)
        self.assertFalse(tags)
        self.assertNotIn('Kappa', tags)
        self.assertNotIn(IrcMessageTagsKey('Kappa'), tags)
        self.assertEqual(str(tags), '')
        self.assertEqual(tags, IrcMessageTagsReadOnly(None))
        self.assertEqual(tags, {})

    def test_empty_instance_mapping_methods(self):
        tags = IrcMessageTagsReadOnly()
        self.assertEqual(tags, tags)
        self.assertEqual(tags, IrcMessageTagsReadOnly())
        self.assertEqual(tags, {})
        self.assertFalse(tags.keys())
        self.assertFalse(tags.values())
        self.assertFalse(tags.items())
        self.assertIsNone(tags.get('Kappa'))
        keyIter = iter(tags)
        self.assertRaises(StopIteration, next, keyIter)

    def test_index_bytes(self):
        tags = IrcMessageTagsReadOnly()
        with self.assertRaises(TypeError):
            b'Kappa' in tags
        with self.assertRaises(TypeError):
            t = tags[b'Kappa']

    def test_index_int(self):
        tags = IrcMessageTagsReadOnly()
        with self.assertRaises(TypeError):
            1 in tags
        with self.assertRaises(TypeError):
            t = tags[1]

    def test_index_missing_str(self):
        tags = IrcMessageTagsReadOnly()
        with self.assertRaises(KeyError):
            t = tags['Kappa']

    def test_index_missing_tagskey(self):
        tags = IrcMessageTagsReadOnly()
        with self.assertRaises(KeyError):
            t = tags[IrcMessageTagsKey('Kappa')]

    def test_readonly(self):
        tags = IrcMessageTagsReadOnly()
        with self.assertRaises(TypeError):
            tags['Kappa'] = 'KappaHD'

    def test_instance_one_item_key_str_value(self):
        tags = IrcMessageTagsReadOnly({'Kappa': 'KappaHD'})
        self.assertEqual(len(tags), 1)
        self.assertTrue(tags)
        self.assertIn('Kappa', tags)
        self.assertIn(IrcMessageTagsKey('Kappa'), tags)
        self.assertEqual(tags['Kappa'], 'KappaHD')
        self.assertEqual(tags[IrcMessageTagsKey('Kappa')], 'KappaHD')
        self.assertEqual(tags,
                         IrcMessageTagsReadOnly(
                             [[IrcMessageTagsKey('Kappa'), 'KappaHD']]))
        self.assertEqual(tags, {'Kappa': 'KappaHD'})

    def test_instance_one_item_vendor_key_true_value(self):
        tags = IrcMessageTagsReadOnly(['turbo/miniK'])
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags['turbo/miniK'], True)
        self.assertEqual(tags, {'turbo/miniK': True})
        self.assertEqual(tags, {IrcMessageTagsKey('miniK', 'turbo'): True})
        self.assertEqual(tags, IrcMessageTagsReadOnly([IrcMessageTagsKey('miniK', 'turbo')]))

    def test_instance_special_values(self):
        tags = IrcMessageTagsReadOnly({'abc': r';\ '})
        self.assertEqual(str(tags), r'abc=\:\\\s')

    def test_instaance_one_item_mapping_methods(self):
        tags = IrcMessageTagsReadOnly(['Kappa'])
        self.assertEqual(tags, tags)
        self.assertEqual(tags, IrcMessageTagsReadOnly({'Kappa': True}))
        self.assertEqual(tags, {'Kappa': True})
        self.assertEqual(len(tags.keys()), 1)
        self.assertEqual(len(tags.values()), 1)
        self.assertEqual(len(tags.items()), 1)
        self.assertIn('Kappa', tags.keys())
        self.assertIn(IrcMessageTagsKey('Kappa'), tags.keys())
        self.assertIn(True, tags.values())
        self.assertIn(('Kappa', True), tags.items())
        self.assertIn((IrcMessageTagsKey('Kappa'), True), tags.items())
        keyIter = iter(tags)
        self.assertEqual(next(keyIter), 'Kappa')
        self.assertRaises(StopIteration, next, keyIter)

    def test_instance_two_items(self):
        tags = IrcMessageTagsReadOnly(['KevinTurtle',
                                       [IrcMessageTagsKey('KreyGasm'), 'PogChamp ']])
        self.assertEqual(len(tags), 2)
        self.assertTrue(tags)
        self.assertIn('KevinTurtle', tags)
        self.assertIn(IrcMessageTagsKey('KreyGasm'), tags)
        self.assertEqual(tags[IrcMessageTagsKey('KevinTurtle')], True)
        self.assertEqual(tags['KreyGasm'], 'PogChamp ')
        strTags = str(tags)
        self.assertIn(strTags, [r'KevinTurtle;KreyGasm=PogChamp\s',
                                r'KreyGasm=PogChamp\s;KevinTurtle'])
        self.assertEqual(tags,
                         IrcMessageTagsReadOnly(
                             {IrcMessageTagsKey('KevinTurtle'): True,
                              'KreyGasm': 'PogChamp '}))

    def test_instance_multi_items(self):
        tags = IrcMessageTagsReadOnly(['KevinTurtle',
                                       IrcMessageTagsKey('PraiseIt'),
                                       ['Kappa', 'Keepo'],
                                       [IrcMessageTagsKey('SwiftRage'), 'DansGame']])
        self.assertEqual(len(tags), 4)
        self.assertEqual(tags['KevinTurtle'], True)
        self.assertEqual(tags['PraiseIt'], True)
        self.assertEqual(tags[IrcMessageTagsKey('Kappa')], 'Keepo')
        self.assertEqual(tags[IrcMessageTagsKey('SwiftRage')], 'DansGame')

    def test_format_values(self):
        self.assertEqual(IrcMessageTagsReadOnly.formatValue('abc'), r'abc')
        self.assertEqual(IrcMessageTagsReadOnly.formatValue('a b c'), r'a\sb\sc')
        self.assertEqual(IrcMessageTagsReadOnly.formatValue('a b c'), r'a\sb\sc')
        self.assertEqual(IrcMessageTagsReadOnly.formatValue('a;b;c'), r'a\:b\:c')
        self.assertEqual(IrcMessageTagsReadOnly.formatValue('a\rb\nc'), r'a\rb\nc')

    def test_str_magic_empty_instance(self):
        self.assertEqual(str(IrcMessageTagsReadOnly()), '')

    def test_str_magic_one_item_with_value_str(self):
        self.assertEqual(
            str(IrcMessageTagsReadOnly({'Kappa': 'KappaPride'})),
            'Kappa=KappaPride')

    def test_str_magic_one_item_with_value(self):
        self.assertEqual(
            str(IrcMessageTagsReadOnly([IrcMessageTagsKey(vendor='twitch.tv', key='KappaHD')])),
            'twitch.tv/KappaHD')

    def test_str_magic_two_items_mixed(self):
        self.assertIn(
            str(IrcMessageTagsReadOnly(
                {'KevinTurtle': True,
                 'SwiftRage/DansGame': 'BibleThump'})),
            ['KevinTurtle;SwiftRage/DansGame=BibleThump',
             'SwiftRage/DansGame=BibleThump;KevinTurtle'])

    def test_str_magic_three_items(self):
        self.assertIn(
            str(IrcMessageTagsReadOnly(
                {'FrankerZ': 'RalpherZ',
                 'TriHard/WinWaker': True,
                 'DatSheffy': True})),
            ['FrankerZ=RalpherZ;TriHard/WinWaker;DatSheffy',
             'FrankerZ=RalpherZ;DatSheffy;TriHard/WinWaker',
             'TriHard/WinWaker;FrankerZ=RalpherZ;DatSheffy',
             'TriHard/WinWaker;DatSheffy;FrankerZ=RalpherZ',
             'DatSheffy;FrankerZ=RalpherZ;TriHard/WinWaker',
             'DatSheffy;TriHard/WinWaker;FrankerZ=RalpherZ'])

    def test_parse_none(self):
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.parseTags, None)

    def test_parse_int(self):
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.parseTags, 1)

    def test_parse_list(self):
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.parseTags, [])

    def test_parse_tuple(self):
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.parseTags, ())

    def test_parse_bytes(self):
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.parseTags, b'')

    def test_parse_key_space(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ' ')

    def test_parse_key_null_char(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, '\0')

    def test_parse_key_cr(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, '\r')

    def test_parse_key_nl(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, '\n')

    def test_parse_key_leading_space(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ' a')

    def test_parse_key_trailing_space(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a ')

    def test_parse_key_covering_space(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ' a ')

    def test_parse_key_opening_parenthesis(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, '(')

    def test_parse_key_closing_parenthesis(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ')')

    def test_parse_key_opening_bracket(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, '[')

    def test_parse_key_closing_bracket(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ']')

    def test_parse_value_space(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a= ')

    def test_parse_value_cr(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a=\r')

    def test_parse_value_nl(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a=\n')

    def test_parse_value_backslash(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a=\\')

    def test_parse_value_null_char(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a=\0')

    def test_parse_empty_elements(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ';')

    def test_parse_trailing_empty_element(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a;')

    def test_parse_leading_empty_element(self):
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ';a')

    def test_parse_empty(self):
        items = IrcMessageTagsReadOnly.parseTags('')
        self.assertIsInstance(items, Dict[IrcMessageTagsKey, TagValue])
        self.assertEqual(items, IrcMessageTagsReadOnly())

    def test_parse_key(self):
        items = IrcMessageTagsReadOnly.parseTags('Kappa')
        self.assertEqual(items, {'Kappa': True})

    def test_parse_key_vendor(self):
        self.assertEqual(IrcMessageTagsReadOnly.parseTags('Kappa/Keepo'),
                         {'Kappa/Keepo': True})

    def test_parse_key_value(self):
        self.assertEqual(IrcMessageTagsReadOnly.parseTags('Kappa=Kippa'),
                         {'Kappa': 'Kippa'})

    def test_parse_three_items(self):
        self.assertEqual(
            IrcMessageTagsReadOnly.parseTags('Kappa=Kippa;BibleThump;FrankerZ=RalpherZ'),
            {'Kappa': 'Kippa', 'BibleThump': True, 'FrankerZ': 'RalpherZ'})

    def test_parse_twitch_tags(self):
        items = IrcMessageTagsReadOnly.parseTags(
            'badges=broadcaster/1;color=;display-name=BotGotsThis;'
            'emote-sets=0;mod=0;subscriber=0;turbo=0;user-type=')
        self.assertEqual(items['badges'], 'broadcaster/1')
        self.assertEqual(items['color'], '')
        self.assertEqual(items['display-name'], 'BotGotsThis')
        self.assertEqual(items['emote-sets'], '0')
        self.assertEqual(items['mod'], '0')
        self.assertEqual(items['subscriber'], '0')
        self.assertEqual(items['turbo'], '0')
        self.assertEqual(items['user-type'], '')


class TestsIrcTags(unittest.TestCase):
    def test_set_item_none(self):
        tags = IrcMessageTags()
        with self.assertRaises(TypeError):
            tags['Kappa'] = None

    def test_set_item_false(self):
        tags = IrcMessageTags()
        with self.assertRaises(ValueError):
            tags['Kappa'] = False

    def test_set_item_int(self):
        tags = IrcMessageTags()
        with self.assertRaises(TypeError):
            tags['Kappa'] = 0

    def test_set_item_list(self):
        tags = IrcMessageTags()
        with self.assertRaises(TypeError):
            tags['Kappa'] = []

    def test_set_item(self):
        tags = IrcMessageTags()
        self.assertEqual(len(tags), 0)
        tags['Kappa'] = True
        self.assertEqual(len(tags), 1)
        self.assertIn('Kappa', tags)
        self.assertIs(tags['Kappa'], True)

    def test_set_item_str(self):
        tags = IrcMessageTags()
        tags['Kappa'] = 'KappaHD'
        self.assertEqual(tags['Kappa'], 'KappaHD')

    def test_delete_item(self):
        tags = IrcMessageTags({'Kappa': True})
        self.assertEqual(len(tags), 1)
        del tags['Kappa']
        self.assertEqual(len(tags), 0)
        self.assertNotIn('Kappa', tags)

    def test_mutable_mapping(self):
        tags = IrcMessageTags({'Kappa': 'KappaPride'})
        self.assertEqual(tags.pop('Kappa'), 'KappaPride')
        self.assertEqual(len(tags), 0)
        self.assertRaises(KeyError, tags.pop, 'Kappa')
        self.assertEqual(tags.setdefault('Kappa', 'KappaHD'), 'KappaHD')
        self.assertEqual(tags.setdefault('Kappa', 'KappePride'), 'KappaHD')
        self.assertEqual(tags.popitem(), ('Kappa', 'KappaHD'))
        self.assertRaises(KeyError, tags.popitem)
        tags.update(BibleThump=True)
        self.assertEqual(len(tags), 1)
        self.assertIn('BibleThump', tags)
