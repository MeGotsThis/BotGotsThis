import os
from tests.database.sqlite.test_database import TestSqlite


class TestSqliteGameAbbreviation(TestSqlite):
    def setUp(self):
        super().setUp()
        self.execute(['''
CREATE TABLE game_abbreviations (
    abbreviation VARCHAR NOT NULL COLLATE NOCASE PRIMARY KEY,
    twitchGame VARCHAR NOT NULL COLLATE NOCASE
)''','''
CREATE INDEX game_abbreviations_game ON game_abbreviations (twitchGame)'''])
        self.execute('INSERT INTO game_abbreviations VALUES (?, ?)',
                     ('kappa', 'FrankerZ'))

    def test_not_existing(self):
        self.assertIsNone(self.database.getFullGameTitle('kappahd'))

    def test_abbreviation(self):
        self.assertEqual(self.database.getFullGameTitle('kappa'), 'FrankerZ')

    def test_casing(self):
        self.assertEqual(self.database.getFullGameTitle('Kappa'), 'FrankerZ')

    def test_twitch_game(self):
        self.assertEqual(self.database.getFullGameTitle('FrankerZ'), 'FrankerZ')

    def test_twitch_game_casing(self):
        self.assertEqual(self.database.getFullGameTitle('frankerz'), 'FrankerZ')
