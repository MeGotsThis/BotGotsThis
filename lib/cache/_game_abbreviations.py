import json
from typing import Dict, Optional

from ._abc import AbcCacheStore
from .. import database


class GameAbbreviationsMixin(AbcCacheStore):
    async def loadGameAbbreviations(self) -> Dict[str, str]:
        gameAbbreviations: Dict[str, str]
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            gameAbbreviations = {abbr: game async for (abbr, game)
                                 in db.getGameAbbreviations()}
        await self.redis.setex('game-abbreviation', 3600,
                               json.dumps(gameAbbreviations))
        return gameAbbreviations

    async def _getGameAbbreviations(self) -> Dict[str, str]:
        value: Optional[str] = await self.redis.get('game-abbreviation')
        if value is None:
            return await self.loadGameAbbreviations()
        else:
            return json.loads(value)

    async def getFullGameTitle(self, abbreviation: str) -> Optional[str]:
        gameAbbreviations: Dict[str, str] = await self._getGameAbbreviations()
        lowerGames: Dict[str, str]
        lowerGames = {a.lower(): g for a, g in gameAbbreviations.items()}
        lowerAbrrev: str = abbreviation.lower()
        if lowerAbrrev in lowerGames:
            return lowerGames[lowerAbrrev]
        game: str
        for game in gameAbbreviations.values():
            if game.lower() == lowerAbrrev:
                return game
        return None

    async def resetGameAbbreviations(self) -> None:
        await self.redis.delete('game-abbreviation')
