from typing import Any, AsyncIterator, Optional, Tuple  # noqa: F401

import aioodbc.cursor  # noqa: F401

from ._base import Database


class GameAbbreviationsMixin(Database):
    async def getGameAbbreviations(self) -> AsyncIterator[Tuple[str, str]]:
        query: str = '''
SELECT abbreviation, twitchGame
    FROM game_abbreviations
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            async for abbr, game in await cursor.execute(query):
                yield abbr, game

    async def getFullGameTitle(self, abbreviation: str) -> Optional[str]:
        query: str = '''
SELECT DISTINCT twitchGame, LOWER(twitchGame)=? AS isGame
    FROM game_abbreviations
    WHERE LOWER(abbreviation)=?
        OR LOWER(twitchGame)=?
    ORDER BY isGame DESC
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (abbreviation.lower(),) * 3)
            game: Optional[Tuple[str]] = await cursor.fetchone()
            return game and game[0]
