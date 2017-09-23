import unittest

from lib.helper import parser


class TestLibraryParser(unittest.TestCase):
    def test(self):
        self.assertEqual(parser.parseArguments('a b c'), ['a', 'b', 'c'])

    def test_complex(self):
        self.assertEqual(parser.parseArguments('a "b c" d'), ['a', 'b c', 'd'])

    def test_mixed(self):
        self.assertEqual(
            parser.parseArguments('a b"c d" e'), ['a', 'bc d', 'e'])
        self.assertEqual(
            parser.parseArguments('a b "c d"e'), ['a', 'b', 'c de'])
        self.assertEqual(
            parser.parseArguments('a b"c d"e'), ['a', 'bc de'])

    def test_single_quote(self):
        self.assertEqual(parser.parseArguments('a "b c'), ['a', 'b c'])

    def test_escape(self):
        self.assertEqual(parser.parseArguments(r'a \"b c'), ['a', '"b', 'c'])
        self.assertEqual(
            parser.parseArguments(r'a "b \" c" d'), ['a', 'b " c', 'd'])
        self.assertEqual(parser.parseArguments('a b c\\'), ['a', 'b', 'c\\'])
        self.assertEqual(parser.parseArguments(r'a \b c'), ['a', r'\b', 'c'])
