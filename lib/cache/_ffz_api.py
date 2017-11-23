import asyncio
import json
from typing import Awaitable, Dict, List, Optional, Tuple  # noqa: F401

from ._abc import AbcCacheStore
from ..api import ffz


class FrankerFaceZApisMixin(AbcCacheStore):
    def _ffzGlobalEmoteKey(self) -> str:
        return 'emote:ffz'

    async def ffz_load_global_emotes(self, *, background: bool=False) -> bool:
        key: str = self._ffzGlobalEmoteKey()
        ttl: int = await self.redis.ttl(key)
        if ttl >= 30 and background:
            return True
        if ttl >= 0 and not background:
            return True
        emotes: Optional[Dict[int, str]]
        emotes = await ffz.getGlobalEmotes()
        if emotes is None:
            return False
        await self.ffz_save_global_emotes(emotes)
        return True

    async def ffz_save_global_emotes(self, emotes: Dict[int, str]) -> bool:
        await self.redis.setex(self._ffzGlobalEmoteKey(), 3600,
                               json.dumps(emotes))
        return True

    async def ffz_get_global_emotes(self) -> Optional[Dict[int, str]]:
        key: str = self._ffzGlobalEmoteKey()
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return None
        return {int(i): e for i, e in json.loads(value).items()}

    def _ffzBroadcasterEmoteKey(self, broadcaster: str) -> str:
        return f'emote:ffz:{broadcaster}'

    async def ffz_load_broadcaster_emotes(self, broadcaster: str, *,
                                          background: bool=False) -> bool:
        key: str = self._ffzBroadcasterEmoteKey(broadcaster)
        ttl: int = await self.redis.ttl(key)
        if ttl >= 30 and background:
            return True
        if ttl >= 0 and not background:
            return True
        emotes: Optional[Dict[int, str]] = {}
        emotes = await ffz.getBroadcasterEmotes(broadcaster)
        if emotes is None:
            return False
        await self.ffz_save_broadcaster_emotes(broadcaster, emotes)
        return True

    async def ffz_save_broadcaster_emotes(self, broadcaster: str,
                                          emotes: Dict[int, str]) -> bool:
        await self.redis.setex(self._ffzBroadcasterEmoteKey(broadcaster), 3600,
                               json.dumps(emotes))
        return True

    async def ffz_get_broadcaster_emotes(self, broadcaster: str
                                         ) -> Optional[Dict[int, str]]:
        key: str = self._ffzBroadcasterEmoteKey(broadcaster)
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return None
        return {int(i): e for i, e in json.loads(value).items()}

    async def ffz_get_cached_broadcasters(self) -> Dict[str, int]:
        keys: List[str] = []
        cur: bytes = b'0'
        ckeys: List[bytes]
        while cur:
            cur, ckeys = await self.redis.scan(cur, match='emote:ffz:*')
            keys.extend(k.decode() for k in ckeys)
        ttlValues: Tuple[int, ...] = await asyncio.gather(
            *[self.redis.ttl(key) for key in keys]
        )
        return {key[10:]: ttl for key, ttl in zip(keys, ttlValues)}
