import json
from typing import Optional

from ._abc import AbcCacheStore
from ..api import twitch


class TwitchApisMixin(AbcCacheStore):
    async def twitch_num_followers(self, user: str) -> Optional[int]:
        key: str = f'twitch:{user}:following'
        numFollowers: Optional[int]
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            numFollowers = await twitch.num_followers(user)
            expire: int = 3600 if numFollowers else 300
            await self.redis.setex(key, expire, json.dumps(numFollowers))
        else:
            numFollowers = json.loads(value)
        return numFollowers
