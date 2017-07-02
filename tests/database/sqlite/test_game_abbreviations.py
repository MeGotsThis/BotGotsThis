from tests.database.sqlite.test_database import TestSqlite
from tests.database.tests.test_game_abbreviations import TestGameAbbreviation


class TestSqliteGameAbbreviation(TestGameAbbreviation, TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.execute(['''
CREATE TABLE game_abbreviations (
    abbreviation VARCHAR NOT NULL COLLATE NOCASE PRIMARY KEY,
    twitchGame VARCHAR NOT NULL COLLATE NOCASE
)''', '''
CREATE INDEX game_abbreviations_game ON game_abbreviations (twitchGame)'''])
        await self.execute('INSERT INTO game_abbreviations VALUES (?, ?)',
                           ('kappa', 'FrankerZ'))
