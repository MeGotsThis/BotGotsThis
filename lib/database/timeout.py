from typing import Optional, cast

import aioodbc.cursor  # noqa: F401
import pyodbc

import bot
from ._base import Database


class DatabaseTimeout(Database):
    async def __aenter__(self) -> 'DatabaseTimeout':
        return cast(DatabaseTimeout, await super().__aenter__())

    @staticmethod
    def acquire() -> 'DatabaseTimeout':
        return DatabaseTimeout(bot.globals.connectionPools['timeout'])

    async def recordTimeout(self,
                            broadcaster: str,
                            user: str,
                            fromUser: Optional[str],
                            module: str,
                            level: Optional[int],
                            length: Optional[int],
                            message: Optional[str],
                            reason: Optional[str]) -> bool:
        query: str = '''
INSERT INTO timeout_logs
    (broadcaster, twitchUser, fromUser, module, level, length, message, reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                await cursor.execute(query, (broadcaster, user, fromUser,
                                             module, level, length, message,
                                             reason))
                await self.commit()
                return True
            except pyodbc.Error:
                return False
