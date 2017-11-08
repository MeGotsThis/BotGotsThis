from typing import Any, Optional, Tuple, cast  # noqa: F401

import aioodbc.cursor  # noqa: F401

import bot
from ._base import Database


class DatabaseOAuth(Database):
    async def __aenter__(self) -> 'DatabaseOAuth':
        return cast(DatabaseOAuth, await super().__aenter__())

    @staticmethod
    def acquire() -> 'DatabaseOAuth':
        return DatabaseOAuth(bot.globals.connectionPools['oauth'])

    async def getOAuthToken(self, broadcaster: str) -> Optional[str]:
        query: str = 'SELECT token FROM oauth_tokens WHERE broadcaster=?'
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster,))
            token: Optional[Tuple[str]] = await cursor.fetchone()
            return token and token[0]

    async def saveBroadcasterToken(self,
                                   broadcaster: str,
                                   token: str) -> None:
        query: str
        params: Tuple[Any, ...]
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            if self.isSqlite:
                query = '''
REPLACE INTO oauth_tokens (broadcaster, token) VALUES (?, ?)
'''
                params = broadcaster, token
            else:
                query = '''
INSERT INTO oauth_tokens (broadcaster, token) VALUES (?, ?)
    ON CONFLICT ON CONSTRAINT oauth_tokens_pkey
    DO UPDATE SET token=?
'''
                params = broadcaster, token, token
            await cursor.execute(query, params)
        await self.commit()
