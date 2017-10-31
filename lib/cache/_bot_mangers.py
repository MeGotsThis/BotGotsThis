import json
from typing import List, Optional  # noqa: F401

from ._abc import AbcCacheStore
from .. import database


class BotManagersMixin(AbcCacheStore):
    async def isBotManager(self, user: str) -> bool:
        managers: List[str]
        value: Optional[str] = await self.redis.get('managers')
        if value is None:
            db: database.DatabaseMain
            async with database.get_main_database() as db:
                managers = [m async for m in db.getBotManagers()]
            await self.redis.setex('managers', 3600, json.dumps(managers))
        else:
            managers = json.loads(value)
        return user in managers

    async def resetBotManagers(self) -> None:
        await self.redis.delete('managers')

    async def addBotManager(self, user: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.addBotManager(user)
        if val:
            await self.resetBotManagers()
        return val

    async def removeBotManager(self, user: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.removeBotManager(user)
        if val:
            await self.resetBotManagers()
        return val
