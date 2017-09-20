import unittest
from unittest.mock import patch

from source.helper import message


def send(messages):
    pass


def method(args):
    return True


class TestLibraryMessage(unittest.TestCase):
    def setUp(self):
        patcher = patch('bot.config')
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.messageLimit = 30

    def test(self):
        self.assertEqual(list(message.messagesFromItems([])), [])

    def test_one_item(self):
        self.assertEqual(list(message.messagesFromItems(['a'])), ['a'])

    def test_two_items(self):
        self.assertEqual(
            list(message.messagesFromItems(['a', 'b'])), ['a, b'])

    def test_too_many_items(self):
        self.assertEqual(
            list(message.messagesFromItems(['a'] * 11)),
            ['a, ' * 9 + 'a', 'a'])

    def test_too_many_many_items(self):
        self.assertEqual(
            list(message.messagesFromItems(['a'] * 31)),
            ['a, ' * 9 + 'a'] * 3 + ['a'])

    def test_prepend(self):
        self.assertEqual(list(message.messagesFromItems([], 'Items: ')), [])

    def test_prepend_one_item(self):
        self.assertEqual(
            list(message.messagesFromItems(['a'], 'Items: ')), ['Items: a'])

    def test_prepend_too_many_items(self):
        self.assertEqual(
            list(message.messagesFromItems(['a'] * 9, 'Items: ')),
            ['Items: ' + 'a, ' * 7 + 'a', 'Items: a'])
