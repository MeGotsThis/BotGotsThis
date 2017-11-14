from types import TracebackType  # noqa: F401
from typing import Optional, Type

import aioredis

from ._auto_repeat import AutoRepeatMixin
from ._bot_mangers import BotManagersMixin
from ._chat_properties import ChatPropertiesMixin
from ._custom_commands import CustomCommandsMixin
from ._ffz_api import FrankerFaceZApisMixin
from ._features import FeaturesMixin
from ._game_abbreviations import GameAbbreviationsMixin
from ._permitted_users import PermittedUsersMixin
from ._twitch_api import TwitchApisMixin


class CacheStore(FeaturesMixin, ChatPropertiesMixin, PermittedUsersMixin,
                 BotManagersMixin, CustomCommandsMixin, AutoRepeatMixin,
                 GameAbbreviationsMixin, TwitchApisMixin,
                 FrankerFaceZApisMixin):
    def __init__(self,
                 pool: aioredis.ConnectionsPool) -> None:
        super().__init__()
        self._pool: aioredis.ConnectionsPool = pool
        self._connection: Optional[aioredis.RedisConnection] = None
        self._redis: Optional[aioredis.Redis] = None

    @property
    def redis(self) -> aioredis.Redis:
        if self._redis is None:
            raise ConnectionError('CacheStore not connected')
        return self._redis

    async def open(self) -> None:
        self._connection = await self._pool.acquire()
        self._redis = aioredis.Redis(self._connection)

    async def close(self) -> None:
        if self._connection is not None:
            self._pool.release(self._connection)
            self._connection = None
            self._redis = None

    async def __aenter__(self) -> 'CacheStore':
        await self.open()
        return self

    async def __aexit__(self,
                        type: Optional[Type[BaseException]],
                        value: Optional[BaseException],
                        traceback: Optional[TracebackType]) -> None:
        await self.close()
