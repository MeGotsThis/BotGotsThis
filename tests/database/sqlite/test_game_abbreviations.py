import os
from tests.database.sqlite.test_database import TestSqlite


class TestSqliteGameAbbreviation(TestSqlite):
    def setUp(self):
        super().setUp()
        self.execute('''
CREATE TABLE game_abbreviations (
    abbreviation VARCHAR NOT NULL PRIMARY KEY,
    twitchGame VARCHAR NOT NULL
)''')

    def test_get(self):
        self.assertIsNone(self.database.getFullGameTitle('kappa'))

    def test_get_existing(self):
        self.execute('INSERT INTO game_abbreviations VALUES (?, ?)',
                     ('kappa', 'FrankerZ'))
        self.assertEqual(self.database.getFullGameTitle('kappa'), 'FrankerZ')
