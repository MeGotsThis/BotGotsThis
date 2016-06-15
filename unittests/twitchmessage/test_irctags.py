import unittest
from typing import Dict
from bot.twitchmessage import IrcMessageTags, IrcMessageTagsKey
from bot.twitchmessage import IrcMessageTagsReadOnly
from bot.twitchmessage._irctags import TagValue


class TestsIrcTagsReadOnly(unittest.TestCase):
    def test_keys(self):
        key = IrcMessageTagsReadOnly.fromKey('')
        self.assertIsInstance(key, IrcMessageTagsKey)
        self.assertEqual(key, IrcMessageTagsKey())
        self.assertEqual(key, '')

        key = IrcMessageTagsReadOnly.fromKey('Kappa')
        self.assertEqual(key, IrcMessageTagsKey('Kappa'))
        self.assertEqual(key, 'Kappa')

        key = IrcMessageTagsReadOnly.fromKey('Kappa/Keepo')
        self.assertEqual(key, IrcMessageTagsKey('Keepo', 'Kappa'))
        self.assertEqual(key, 'Kappa/Keepo')

        self.assertRaises(TypeError, IrcMessageTagsReadOnly.fromKey, None)
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.fromKey, 1)
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.fromKey, b'')

    def test_except_on_constructor(self):
        self.assertRaises(TypeError, IrcMessageTagsReadOnly, 1)
        self.assertRaises(TypeError, IrcMessageTagsReadOnly, IrcMessageTagsKey())

    def test_empty_instance(self):
        tags = IrcMessageTagsReadOnly()
        self.assertEqual(len(tags), 0)
        self.assertFalse(tags)
        self.assertFalse(tags.keys())
        self.assertFalse(tags.values())
        self.assertFalse(tags.items())
        self.assertNotIn('Kappa', tags)
        self.assertNotIn(IrcMessageTagsKey('Kappa'), tags)
        with self.assertRaises(TypeError):
            b'Kappa' in tags
        with self.assertRaises(KeyError):
            t = tags['Kappa']
        with self.assertRaises(KeyError):
            t = tags[IrcMessageTagsKey('Kappa')]
        with self.assertRaises(TypeError):
            t = tags[b'Kappa']
        with self.assertRaises(TypeError):
            t = tags[1]
        with self.assertRaises(TypeError):
            tags['Kappa'] = 'KappaHD'
        self.assertEqual(str(tags), '')
        self.assertIs(tags, IrcMessageTagsReadOnly(tags))
        self.assertEqual(tags, IrcMessageTagsReadOnly(None))
        self.assertEqual(tags, {})

    def test_instance(self):
        tags = IrcMessageTagsReadOnly({'Kappa': 'KappaHD'})
        self.assertEqual(len(tags), 1)
        self.assertTrue(tags)
        self.assertEqual(len(tags.keys()), 1)
        self.assertEqual(len(tags.values()), 1)
        self.assertEqual(len(tags.items()), 1)
        self.assertIn('Kappa', tags)
        self.assertIn(IrcMessageTagsKey('Kappa'), tags)
        self.assertIn('Kappa', tags.keys())
        self.assertIn(IrcMessageTagsKey('Kappa'), tags.keys())
        self.assertIn('KappaHD', tags.values())
        self.assertIn(('Kappa', 'KappaHD'), tags.items())
        self.assertEqual(tags['Kappa'], 'KappaHD')
        self.assertEqual(tags[IrcMessageTagsKey('Kappa')], 'KappaHD')
        self.assertNotIn('Keepo', tags)
        self.assertNotIn(IrcMessageTagsKey('Keepo'), tags)
        self.assertIsNone(tags.get('Keepo'))
        with self.assertRaises(KeyError):
            t = tags['Keepo']
        with self.assertRaises(KeyError):
            t = tags[IrcMessageTagsKey('Keepo')]
        keyIter = iter(tags)
        self.assertEqual(next(keyIter), 'Kappa')
        self.assertRaises(StopIteration, next, keyIter)
        self.assertEqual(str(tags), 'Kappa=KappaHD')
        self.assertIs(tags, IrcMessageTagsReadOnly(tags))
        self.assertEqual(tags,
                         IrcMessageTagsReadOnly(
                             [[IrcMessageTagsKey('Kappa'), 'KappaHD']]))
        self.assertEqual(tags, {'Kappa': 'KappaHD'})

        tags = IrcMessageTagsReadOnly(['turbo/miniK'])
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags['turbo/miniK'], True)
        self.assertEqual(tags, {'turbo/miniK': True})
        self.assertEqual(tags, {IrcMessageTagsKey('miniK', 'turbo'): True})
        self.assertEqual(tags, IrcMessageTagsReadOnly([IrcMessageTagsKey('miniK', 'turbo')]))

        tags = IrcMessageTagsReadOnly({'abc': r';\ '})
        self.assertEqual(str(tags), r'abc=\:\\\s')

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

    def test_format_vales(self):
        self.assertEqual(IrcMessageTagsReadOnly.formatValue('abc'), r'abc')
        self.assertEqual(IrcMessageTagsReadOnly.formatValue('a b c'), r'a\sb\sc')
        self.assertEqual(IrcMessageTagsReadOnly.formatValue('a b c'), r'a\sb\sc')
        self.assertEqual(IrcMessageTagsReadOnly.formatValue('a;b;c'), r'a\:b\:c')
        self.assertEqual(IrcMessageTagsReadOnly.formatValue('a\rb\nc'), r'a\rb\nc')

    def test_parse(self):
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.parseTags, None)
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.parseTags, 1)
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.parseTags, [])
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.parseTags, ())
        self.assertRaises(TypeError, IrcMessageTagsReadOnly.parseTags, b'')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ' ')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, '\0')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, '\r')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, '\n')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ' a')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a ')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ' a ')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, '(')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ')')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, '[')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ']')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ']')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a= ')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a=\r')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a=\n')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a=\\')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a=\0')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ';')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, 'a;')
        self.assertRaises(ValueError, IrcMessageTagsReadOnly.parseTags, ';a')

        self.assertEqual(IrcMessageTagsReadOnly.parseTags(''),
                         IrcMessageTagsReadOnly())

        items = IrcMessageTagsReadOnly.parseTags('Kappa')
        self.assertIsInstance(items, Dict[IrcMessageTagsKey, TagValue])
        self.assertEqual(items, {'Kappa': True})
        self.assertEqual(items, IrcMessageTagsReadOnly(['Kappa']))

        self.assertEqual(IrcMessageTagsReadOnly.parseTags('Kappa/Keepo'),
                         {IrcMessageTagsKey('Keepo', 'Kappa'): True})
        self.assertEqual(IrcMessageTagsReadOnly.parseTags('Kappa/Keepo'),
                         {'Kappa/Keepo': True})
        self.assertEqual(IrcMessageTagsReadOnly.parseTags('Kappa=Kippa'),
                         {'Kappa': 'Kippa'})
        self.assertEqual(
            IrcMessageTagsReadOnly.parseTags('Kappa=Kippa;BibleThump;FrankerZ=RalpherZ'),
            {'Kappa': 'Kippa', 'BibleThump': True, 'FrankerZ': 'RalpherZ'})

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
    def test(self):
        tags = IrcMessageTags()
        self.assertEqual(len(tags), 0)
        self.assertFalse(tags)
        self.assertFalse(tags.keys())
        self.assertFalse(tags.values())
        self.assertFalse(tags.items())
        self.assertNotIn('Kappa', tags)
        self.assertNotIn(IrcMessageTagsKey('Kappa'), tags)
        with self.assertRaises(TypeError):
            b'Kappa' in tags
        with self.assertRaises(KeyError):
            t = tags['Kappa']
        with self.assertRaises(KeyError):
            t = tags[IrcMessageTagsKey('Kappa')]
        with self.assertRaises(TypeError):
            t = tags[b'Kappa']
        with self.assertRaises(TypeError):
            t = tags[1]
        with self.assertRaises(KeyError):
            tags.pop('Kappa')
        with self.assertRaises(KeyError):
            tags.popitem()
        self.assertEqual(str(tags), '')
        self.assertIsNot(tags, IrcMessageTags(tags))
        self.assertIsNot(tags, IrcMessageTagsReadOnly(tags))
        self.assertEqual(tags, IrcMessageTags(None))
        self.assertEqual(tags, IrcMessageTagsReadOnly(None))
        self.assertEqual(tags, {})

        tags['Kappa'] = 'KappaHD'
        self.assertEqual(len(tags), 1)
        self.assertTrue(tags)
        self.assertTrue(tags.keys())
        self.assertTrue(tags.values())
        self.assertTrue(tags.items())
        self.assertEqual(len(tags.keys()), 1)
        self.assertEqual(len(tags.values()), 1)
        self.assertEqual(len(tags.items()), 1)
        self.assertIn('Kappa', tags)
        self.assertIn(IrcMessageTagsKey('Kappa'), tags)
        self.assertIn('Kappa', tags.keys())
        self.assertIn(IrcMessageTagsKey('Kappa'), tags.keys())
        self.assertIn('KappaHD', tags.values())
        self.assertIn(('Kappa', 'KappaHD'), tags.items())
        self.assertEqual(tags['Kappa'], 'KappaHD')
        self.assertEqual(tags[IrcMessageTagsKey('Kappa')], 'KappaHD')
        self.assertNotIn('Keepo', tags)
        self.assertNotIn(IrcMessageTagsKey('Keepo'), tags)
        self.assertIsNone(tags.get('Keepo'))
        with self.assertRaises(KeyError):
            t = tags['Keepo']
        with self.assertRaises(KeyError):
            t = tags[IrcMessageTagsKey('Keepo')]
        keyIter = iter(tags)
        self.assertEqual(next(keyIter), 'Kappa')
        self.assertRaises(StopIteration, next, keyIter)
        self.assertEqual(str(tags), 'Kappa=KappaHD')
        self.assertEqual(tags, IrcMessageTagsReadOnly(tags))
        self.assertEqual(tags,
                         IrcMessageTagsReadOnly(
                             [[IrcMessageTagsKey('Kappa'), 'KappaHD']]))
        self.assertEqual(tags, IrcMessageTags({'Kappa': 'KappaHD'}))
        self.assertEqual(tags, {'Kappa': 'KappaHD'})

        self.assertIs(tags.setdefault('KevinTurtle', True), True)
        self.assertEqual(len(tags), 2)
        self.assertIn('KevinTurtle', tags)
        self.assertEqual(tags['KevinTurtle'], True)

        tags.update(BibleThump='ResidentSleeper')
        self.assertEqual(len(tags), 3)
        self.assertIn('BibleThump', tags)
        self.assertEqual(tags['BibleThump'], 'ResidentSleeper')

        del tags['Kappa']
        self.assertEqual(len(tags), 2)
        self.assertIn('KevinTurtle', tags)
        self.assertIn('BibleThump', tags)
        self.assertNotIn('Kappa', tags)

        tags.clear()
        self.assertEqual(len(tags), 0)
        self.assertNotIn('Kappa', tags)
        self.assertNotIn('KevinTurtle', tags)
        self.assertNotIn('BibleThump', tags)



