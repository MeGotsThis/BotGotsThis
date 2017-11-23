import asyncio
import json
from typing import Awaitable, Dict, List, Optional, Tuple  # noqa: F401

from ._abc import AbcCacheStore
from ..api import bttv


class BetterTwitchTvApisMixin(AbcCacheStore):
    def _bttvGlobalEmoteKey(self) -> str:
        return 'emote:bttv'

    async def bttv_load_global_emotes(self, *, background: bool=False) -> bool:
        key: str = self._bttvGlobalEmoteKey()
        ttl: int = await self.redis.ttl(key)
        if ttl >= 30 and background:
            return True
        if ttl >= 0 and not background:
            return True
        emotes: Optional[Dict[str, str]]
        emotes = await bttv.getGlobalEmotes()
        if emotes is None:
            return False
        await self.bttv_save_global_emotes(emotes)
        return True

    async def bttv_save_global_emotes(self, emotes: Dict[str, str]) -> bool:
        await self.redis.setex(self._bttvGlobalEmoteKey(), 3600,
                               json.dumps(emotes))
        return True

    async def bttv_get_global_emotes(self) -> Optional[Dict[str, str]]:
        key: str = self._bttvGlobalEmoteKey()
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    def _bttvBroadcasterEmoteKey(self, broadcaster: str) -> str:
        return f'emote:bttv:{broadcaster}'

    async def bttv_load_broadcaster_emotes(self, broadcaster: str, *,
                                           background: bool=False) -> bool:
        key: str = self._bttvBroadcasterEmoteKey(broadcaster)
        ttl: int = await self.redis.ttl(key)
        if ttl >= 30 and background:
            return True
        if ttl >= 0 and not background:
            return True
        emotes: Optional[Dict[str, str]] = {}
        emotes = await bttv.getBroadcasterEmotes(broadcaster)
        if emotes is None:
            return False
        await self.bttv_save_broadcaster_emotes(broadcaster, emotes)
        return True

    async def bttv_save_broadcaster_emotes(self, broadcaster: str,
                                           emotes: Dict[str, str]) -> bool:
        await self.redis.setex(self._bttvBroadcasterEmoteKey(broadcaster),
                               3600, json.dumps(emotes))
        return True

    async def bttv_get_broadcaster_emotes(self, broadcaster: str
                                          ) -> Optional[Dict[str, str]]:
        key: str = self._bttvBroadcasterEmoteKey(broadcaster)
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def bttv_get_cached_broadcasters(self) -> Dict[str, int]:
        keys: List[str] = []
        cur: bytes = b'0'
        ckeys: List[bytes]
        while cur:
            cur, ckeys = await self.redis.scan(cur, match='emote:bttv:*')
            keys.extend(k.decode() for k in ckeys)
        ttlValues: Tuple[int, ...] = await asyncio.gather(
            *[self.redis.ttl(key) for key in keys]
        )
        return {key[10:]: ttl for key, ttl in zip(keys, ttlValues)}
