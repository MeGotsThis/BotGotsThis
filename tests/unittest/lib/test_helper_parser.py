import unittest

from lib.helper import parser


class TestLibraryParserParseArguments(unittest.TestCase):
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


class TestLibraryParserGetResponse(unittest.TestCase):
    def test(self):
        self.assertEqual(parser.get_response(''), parser.Response.Unknown)

    def test_default(self):
        self.assertEqual(
            parser.get_response('', default=parser.Response.Yes),
            parser.Response.Yes)
        self.assertEqual(
            parser.get_response('', default=parser.Response.No),
            parser.Response.No)

    def test_unknown(self):
        self.assertEqual(parser.get_response('Kappa'), parser.Response.Unknown)

    def test_yes(self):
        self.assertEqual(parser.get_response('yes'), parser.Response.Yes)
        self.assertEqual(parser.get_response('y'), parser.Response.Yes)
        self.assertEqual(parser.get_response('true'), parser.Response.Yes)
        self.assertEqual(parser.get_response('t'), parser.Response.Yes)
        self.assertEqual(parser.get_response('enable'), parser.Response.Yes)
        self.assertEqual(parser.get_response('e'), parser.Response.Yes)
        self.assertEqual(parser.get_response('on'), parser.Response.Yes)
        self.assertEqual(parser.get_response('1'), parser.Response.Yes)

    def test_no(self):
        self.assertEqual(parser.get_response('no'), parser.Response.No)
        self.assertEqual(parser.get_response('n'), parser.Response.No)
        self.assertEqual(parser.get_response('false'), parser.Response.No)
        self.assertEqual(parser.get_response('f'), parser.Response.No)
        self.assertEqual(parser.get_response('disable'), parser.Response.No)
        self.assertEqual(parser.get_response('d'), parser.Response.No)
        self.assertEqual(parser.get_response('off'), parser.Response.No)
        self.assertEqual(parser.get_response('0'), parser.Response.No)
