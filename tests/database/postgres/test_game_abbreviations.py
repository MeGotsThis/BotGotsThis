from tests.database.postgres.test_database import TestPostgres
from tests.database.tests.test_game_abbreviations import TestGameAbbreviation


class TestPostgresGameAbbreviation(TestGameAbbreviation, TestPostgres):
    async def setUp(self):
        await super().setUp()
        await self.execute(['''
CREATE TABLE game_abbreviations (
    abbreviation VARCHAR NOT NULL PRIMARY KEY,
    twitchGame VARCHAR NOT NULL
)''', '''
CREATE INDEX game_abbreviations_game ON game_abbreviations (twitchGame)'''])
        await self.execute('INSERT INTO game_abbreviations VALUES (?, ?)',
                           ('kappa', 'FrankerZ'))
