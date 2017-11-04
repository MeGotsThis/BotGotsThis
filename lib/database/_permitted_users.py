from typing import AsyncIterator

import aioodbc.cursor  # noqa: F401
import pyodbc

from ._base import Database


class PermittedUsersMixin(Database):
    async def getPermittedUsers(self, broadcaster: str) -> AsyncIterator[str]:
        query: str = '''
SELECT twitchUser FROM permitted_users WHERE broadcaster=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            async for user, in await cursor.execute(query, (broadcaster,)):
                yield user

    async def isPermittedUser(self,
                              broadcaster: str,
                              user: str) -> bool:
        query: str = '''
SELECT 1 FROM permitted_users WHERE broadcaster=? AND twitchUser=?
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, user,))
            return bool(await cursor.fetchone())

    async def addPermittedUser(self,
                               broadcaster: str,
                               user: str,
                               moderator: str) -> bool:
        query: str = '''
INSERT INTO permitted_users (broadcaster, twitchUser) VALUES (?, ?)
'''
        history: str = '''
INSERT INTO permitted_users_log
    (broadcaster, twitchUser, moderator, created, actionLog)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                await cursor.execute(query, (broadcaster, user))
            except pyodbc.Error:
                return False

            await cursor.execute(history, (broadcaster, user, moderator,
                                           'add'))
            await self.commit()
            return True

    async def removePermittedUser(self,
                                  broadcaster: str,
                                  user: str,
                                  moderator: str) -> bool:
        query: str = '''
DELETE FROM permitted_users WHERE broadcaster=? AND twitchUser=?
'''
        history: str = '''
INSERT INTO permitted_users_log
    (broadcaster, twitchUser, moderator, created, actionLog)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (broadcaster, user))
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (broadcaster, user, moderator,
                                           'remove'))
            await self.commit()
            return True
