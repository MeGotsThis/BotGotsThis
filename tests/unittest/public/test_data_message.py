import unittest
from source.data import message

class TestDataTokenized(unittest.TestCase):
    def test_none(self):
        self.assertRaises(TypeError, message.Tokenized, None)

    def test_eq(self):
        self.assertEqual(
            message.Tokenized('Kappa \t KappaHD'),
            message.Tokenized('Kappa \t KappaHD'))
        self.assertNotEqual(
            message.Tokenized('Kappa \t KappaHD'),
            message.Tokenized('Kappa    KappaHD'))
        self.assertEqual(
            message.Tokenized('Kappa \t KappaHD'), 'Kappa \t KappaHD')

    def test_hash(self):
        self.assertIsInstance(hash(message.Tokenized('Kappa \t KappaHD')), int)
        self.assertEqual(
            hash(message.Tokenized('Kappa \t KappaHD')),
            hash(message.Tokenized('Kappa \t KappaHD')))

    def test_str(self):
        self.assertEqual(
            str(message.Tokenized('Kappa \t KappaHD')), 'Kappa \t KappaHD')

    def test_len(self):
        self.assertEqual(len(message.Tokenized('Kappa \r\n\tKappaHD')), 2)

    def test_getitem_int(self):
        tokenized = message.Tokenized('Kappa     KappaHD\n\n\n\nKappaPride')
        with self.assertRaises(TypeError):
            tokenized[None]

    def test_getitem_int(self):
        tokenized = message.Tokenized('Kappa     KappaHD\n\n\n\nKappaPride')
        self.assertEqual(tokenized[0], 'Kappa')
        self.assertEqual(tokenized[1], 'KappaHD')
        self.assertEqual(tokenized[2], 'KappaPride')
        self.assertEqual(tokenized[-1], 'KappaPride')
        self.assertEqual(tokenized[-2], 'KappaHD')
        self.assertEqual(tokenized[-3], 'Kappa')
        with self.assertRaises(IndexError):
            tokenized[3]
        with self.assertRaises(IndexError):
            tokenized[-4]

    def test_getitem_slice(self):
        tokenized = message.Tokenized('Kappa  KappaHD  KappaPride  KappaRoss')
        self.assertEqual(tokenized[0:2], 'Kappa  KappaHD')
        self.assertEqual(tokenized[1:], 'KappaHD  KappaPride  KappaRoss')
        self.assertEqual(tokenized[4:], '')
        self.assertEqual(tokenized[:-1], 'Kappa  KappaHD  KappaPride')
        self.assertEqual(tokenized[:-4], '')
        self.assertEqual(tokenized[0:0], '')

class TestDataMessage(unittest.TestCase):
    def test_command(self):
        self.assertEqual(message.Message('!Kappa Keepo').command, '!kappa')

    def test_query(self):
        self.assertEqual(message.Message('!Kappa Keepo').query, 'Keepo')

    def test_lower(self):
        self.assertEqual(
            str(message.Message('!Kappa Keepo').lower), '!kappa keepo')
