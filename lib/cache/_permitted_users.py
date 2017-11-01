import json
from typing import List, Optional  # noqa: F401

from ._abc import AbcCacheStore
from .. import database


class PermittedUsersMixin(AbcCacheStore):
    def _permittedKey(self, broadcaster: str) -> str:
        return f'twitch:{broadcaster}:permitted'

    async def loadPermittedUsers(self, broadcaster: str) -> List[str]:
        key: str = self._permittedKey(broadcaster)
        permittedUsers: List[str]
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            permittedUsers = [user async for user
                              in db.getPermittedUsers(broadcaster)]
        await self.redis.setex(key, 600, json.dumps(permittedUsers))
        return permittedUsers

    async def isPermittedUser(self, broadcaster: str, user: str) -> bool:
        key: str = self._permittedKey(broadcaster)
        permittedUsers: List[str]
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            permittedUsers = await self.loadPermittedUsers(broadcaster)
        else:
            permittedUsers = json.loads(value)
        return user in permittedUsers

    async def resetPermittedUsers(self, broadcaster: str) -> None:
        key: str = self._permittedKey(broadcaster)
        await self.redis.delete(key)

    async def addPermittedUser(self,
                               broadcaster: str,
                               user: str,
                               moderator: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.addPermittedUser(broadcaster, user, moderator)
        if val:
            await self.resetPermittedUsers(broadcaster)
        return val

    async def removePermittedUser(self,
                                  broadcaster: str,
                                  user: str,
                                  moderator: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.removePermittedUser(broadcaster, user, moderator)
        if val:
            await self.resetPermittedUsers(broadcaster)
        return val
