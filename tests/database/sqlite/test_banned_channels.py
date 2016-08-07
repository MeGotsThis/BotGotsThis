from datetime import datetime
from tests.database.sqlite.test_database import TestSqlite
from unittest.mock import ANY


class TestSqliteBannedChannels(TestSqlite):
    def setUp(self):
        super().setUp()
        self.execute(['''
CREATE TABLE banned_channels (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    currentTime TIMESTAMP NOT NULL,
    reason VARCHAR NOT NULL,
    who VARCHAR NOT NULL
)''','''
CREATE TABLE banned_channels_log (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    broadcaster VARCHAR NOT NULL,
    currentTime TIMESTAMP NOT NULL,
    reason VARCHAR NOT NULL,
    who VARCHAR NOT NULL,
    actionLog VARCHAR NOT NULL
)'''])

    def test_list(self):
        self.assertEqual(list(self.database.listBannedChannels()), [])

    def test_list_one(self):
        now = datetime(2000, 1, 1)
        self.execute('INSERT INTO banned_channels VALUES (?, ?, ?, ?)',
                     ('botgotsthis', now, 'Kappa', 'botgotsthis'))
        self.assertEqual(list(self.database.listBannedChannels()),
                         ['botgotsthis'])

    def test_list_multiple(self):
        now = datetime(2000, 1, 1)
        self.executemany('INSERT INTO banned_channels VALUES (?, ?, ?, ?)',
                         [('botgotsthis', now, 'Kappa', 'botgotsthis'),
                          ('megotsthis', now, 'Kappa', 'botgotsthis'),])
        self.assertEqual(list(self.database.listBannedChannels()),
                         ['botgotsthis', 'megotsthis'])

    def test_add(self):
        self.assertIs(
            self.database.addBannedChannel(
                'botgotsthis', 'Kappa', 'megotsthis'),
            True)
        self.assertEqual(self.row('SELECT * FROM banned_channels'),
                         ('botgotsthis', ANY, 'Kappa', 'megotsthis'))
        self.assertEqual(
            self.row('SELECT * FROM banned_channels_log'),
            (ANY, 'botgotsthis', ANY, 'Kappa', 'megotsthis', 'add'))

    def test_add_existing(self):
        now = datetime(2000, 1, 1)
        self.execute('INSERT INTO banned_channels VALUES (?, ?, ?, ?)',
                     ('botgotsthis', now, 'Kappa', 'botgotsthis'))
        self.assertIs(
            self.database.addBannedChannel(
                'botgotsthis', 'Kappa', 'megotsthis'),
            False)
        self.assertIsNone(self.row('SELECT * FROM banned_channels_log'))

    def test_remove(self):
        self.assertIs(
            self.database.removeBannedChannel(
                'botgotsthis', 'Kappa', 'megotsthis'),
            False)

    def test_remove_existing(self):
        now = datetime(2000, 1, 1)
        self.execute('INSERT INTO banned_channels VALUES (?, ?, ?, ?)',
                     ('botgotsthis', now, 'Kappa', 'botgotsthis'))
        self.assertIs(
            self.database.removeBannedChannel(
                'botgotsthis', 'Kappa', 'megotsthis'),
            True)
        self.assertIsNone(self.row('SELECT * FROM banned_channels'))
        self.assertEqual(
            self.row('SELECT * FROM banned_channels_log'),
            (ANY, 'botgotsthis', ANY, 'Kappa', 'megotsthis', 'remove'))
