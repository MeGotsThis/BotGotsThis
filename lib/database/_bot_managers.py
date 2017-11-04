from typing import Any, AsyncIterator, Optional, Tuple, Union  # noqa: F401

import aioodbc.cursor  # noqa: F401
import pyodbc

from ._base import Database


class BotManagersMixin(Database):
    async def getBotManagers(self) -> AsyncIterator[str]:
        query: str = '''SELECT twitchUser FROM bot_managers'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            async for manager, in await cursor.execute(query):
                yield manager

    async def isBotManager(self, user: str) -> bool:
        query: str = '''SELECT 1 FROM bot_managers WHERE twitchUser=?'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (user,))
            return bool(await cursor.fetchone())

    async def addBotManager(self, user: str) -> bool:
        query: str = '''
INSERT INTO bot_managers (twitchUser) VALUES (?)
'''
        history: str = '''
INSERT INTO bot_managers_log
    (twitchUser, created, actionLog)
    VALUES (?, CURRENT_TIMESTAMP, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            try:
                await cursor.execute(query, (user,))
            except pyodbc.Error:
                return False

            await cursor.execute(history, (user, 'add'))
            await self.commit()
            return True

    async def removeBotManager(self, user: str) -> bool:
        query: str = '''
DELETE FROM bot_managers WHERE twitchUser=?
'''
        history: str = '''
INSERT INTO bot_managers_log
    (twitchUser, created, actionLog)
    VALUES (?, CURRENT_TIMESTAMP, ?)
'''
        cursor: aioodbc.cursor.Cursor
        async with await self.cursor() as cursor:
            await cursor.execute(query, (user,))
            if cursor.rowcount == 0:
                return False

            await cursor.execute(history, (user, 'remove'))
            await self.commit()
            return True
