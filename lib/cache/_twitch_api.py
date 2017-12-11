import asyncio
import json
from typing import Any, Awaitable, ClassVar, Dict, Iterable, List, Optional  # noqa: F401,E501
from typing import Set, Tuple, cast

from ._abc import AbcCacheStore
from . import store
from ..api import twitch


class TwitchApisMixin(AbcCacheStore):
    _lastEmoteSet: ClassVar[Optional[Set[int]]] = None

    async def twitch_num_followers(self, user: str) -> Optional[int]:
        key: str = f'twitch:{user}:following'
        numFollowers: Optional[int]
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            data: store.CacheStore = cast(store.CacheStore, self)
            numFollowers = await twitch.num_followers(user, data=data)
            expire: int = 3600 if numFollowers else 300
            await self.redis.setex(key, expire, json.dumps(numFollowers))
        else:
            numFollowers = json.loads(value)
        return numFollowers

    def _twitchIdIdKey(self, id: str) -> str:
        return f'id:id:{id}'

    def _twitchIdUserKey(self, user: str) -> str:
        return f'id:user:{user}'

    async def twitch_load_id(self, user: str) -> bool:
        key: str = self._twitchIdUserKey(user)
        if await self.redis.exists(key):
            return True
        ids: Optional[Dict[str, str]] = await twitch.getTwitchIds([user])
        if ids is None:
            return False
        if user in ids:
            await self.twitch_save_id(ids[user], user)
        else:
            await self.twitch_save_id(None, user)
        return True

    async def twitch_load_ids(self, users: Iterable[str]) -> bool:
        users = list(users)
        existed: Tuple[Optional[str], ...] = await self.redis.mget(
            *(self._twitchIdUserKey(user) for user in users))
        users = [user for user, exists in zip(users, existed) if not exists]
        if not users:
            return True
        ids: Optional[Dict[str, str]] = await twitch.getTwitchIds(users)
        if ids is None:
            return False

        # Save all the new ids and non-existent ids
        await asyncio.gather(
            *[self.twitch_save_id(id, user)
              for user, id in ids.items()],
            *[self.twitch_save_id(None, user)
              for user in users if user not in ids]
        )
        return True

    async def twitch_save_id(self, id: Optional[str], user: str) -> bool:
        # 6 hours normally or 1 hour for non existent id
        expire: int = 21600 if id is not None else 3600
        tasks: List[Awaitable[Any]] = [
            self.redis.setex(self._twitchIdUserKey(user), expire,
                             json.dumps(id)),
        ]
        if id is not None:
            tasks.append(self.redis.setex(self._twitchIdIdKey(id), expire,
                                          json.dumps(user)))
        await asyncio.gather(*tasks)
        return True

    async def twitch_has_id(self, user: str) -> bool:
        key: str = self._twitchIdUserKey(user)
        return await self.redis.exists(key)

    async def twitch_is_valid_user(self, user: str) -> Optional[bool]:
        if not await self.twitch_load_id(user):
            return None
        return await self.twitch_get_id(user) is not None

    async def twitch_get_id(self, user: str) -> Optional[str]:
        key: str = self._twitchIdUserKey(user)
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def twitch_get_ids(self, users: Set[str]
                             ) -> Dict[str, Optional[str]]:
        values: Tuple[Optional[str], ...] = await self.redis.mget(
            *(self._twitchIdUserKey(user) for user in users)
        )
        return dict(zip(users,
                        (json.loads(v) if v is not None else None
                         for v in values)))

    async def twitch_get_user(self, id: str) -> Optional[str]:
        key: str = self._twitchIdIdKey(id)
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    def _twitchCommunityIdKey(self, id: str) -> str:
        return f'community:id:{id}'

    def _twitchCommunityNameKey(self, name: str) -> str:
        return f'community:name:{name.lower()}'

    async def twitch_load_community_id(self, id: str) -> bool:
        key: str = self._twitchCommunityIdKey(id)
        if await self.redis.exists(key):
            return True
        community: Optional[twitch.TwitchCommunity]
        community = await twitch.get_community_by_id(id)
        if community is None:
            return False
        await self.twitch_save_community(community.id, community.name)
        return True

    async def twitch_load_community_ids(self, ids: Set[str]) -> bool:
        if not ids:
            return True
        values: Tuple[Optional[str], ...] = await self.redis.mget(
            *(self._twitchCommunityIdKey(id) for id in ids)
        )
        loadIds: List[str]
        loadIds = [id for id, value in zip(ids, values) if not value]
        if not loadIds:
            return True

        async def load(id: str) -> None:
            community: Optional[twitch.TwitchCommunity]
            community = await twitch.get_community_by_id(id)
            if community is None:
                return
            await self.twitch_save_community(community.id, community.name)

        await asyncio.gather(*(load(id) for id in loadIds))
        return True

    async def twitch_load_community_name(self, name: str) -> bool:
        key: str = self._twitchCommunityNameKey(name)
        if await self.redis.exists(key):
            return True
        community: Optional[twitch.TwitchCommunity]
        community = await twitch.get_community(name)
        if community is None:
            return False
        await self.twitch_save_community(community.id, community.name)
        return True

    async def twitch_save_community(self, id: Optional[str],
                                    name: Optional[str]) -> bool:
        # 6 hours normally or 1 hour for non existent id
        expire: int
        tasks: List[Awaitable[Any]] = []
        if id is not None:
            expire = 21600 if name is not None else 3600
            tasks.append(self.redis.setex(self._twitchCommunityIdKey(id),
                                          expire, json.dumps(name)))
        if name is not None:
            expire = 21600 if id is not None else 3600
            tasks.append(self.redis.setex(self._twitchCommunityNameKey(name),
                                          expire, json.dumps(id)))
        if tasks:
            await asyncio.gather(*tasks)
        return True

    async def twitch_get_community_id(self, name: str) -> Optional[str]:
        key: str = self._twitchCommunityNameKey(name)
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def twitch_get_community_name(self, id: str) -> Optional[str]:
        key: str = self._twitchCommunityIdKey(id)
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    def _twitchEmoteSetKey(self) -> str:
        return f'emote:twitch:set'

    def _twitchEmoteKey(self) -> str:
        return f'emote:twitch'

    async def twitch_load_emotes(self, emote_sets: Set[int], *,
                                 background: bool=False) -> bool:
        if not emote_sets:
            return False
        key: str = self._twitchEmoteKey()
        sameSet: bool = await self.twitch_get_bot_emote_set() == emote_sets
        await self.twitch_save_emote_set(emote_sets)
        if sameSet:
            ttl: int = await self.redis.ttl(key)
            if ttl >= 30 and background:
                return True
            if ttl >= 0 and not background:
                return True
        emotes: Optional[Dict[int, Tuple[str, int]]]
        emotes = await twitch.twitch_emotes(emote_sets)
        if emotes is None:
            return False
        await self.twitch_save_emotes(emotes)
        return True

    async def twitch_save_emote_set(self, emote_sets: Set[int]) -> bool:
        type(self)._lastEmoteSet = set(emote_sets)
        await self.redis.setex(self._twitchEmoteSetKey(), 86400,
                               json.dumps([s for s in emote_sets]))
        return True

    async def twitch_save_emotes(self, emotes: Dict[int, Tuple[str, int]]
                                 ) -> bool:
        await self.redis.setex(self._twitchEmoteKey(), 3600,
                               json.dumps(emotes))
        return True

    async def twitch_get_bot_emote_set(self) -> Optional[Set[int]]:
        key: str = self._twitchEmoteSetKey()
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return type(self)._lastEmoteSet
        return {i for i in json.loads(value)}

    async def twitch_get_emotes(self) -> Optional[Dict[int, str]]:
        key: str = self._twitchEmoteKey()
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return None
        return {int(i): e[0] for i, e in json.loads(value).items()}

    async def twitch_get_emote_sets(self) -> Optional[Dict[int, int]]:
        key: str = self._twitchEmoteKey()
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return None
        return {int(i): e[1] for i, e in json.loads(value).items()}
