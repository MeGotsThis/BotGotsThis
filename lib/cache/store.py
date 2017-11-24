from datetime import datetime
from types import TracebackType  # noqa: F401
from typing import Optional, Type

import aioredis

import bot
from ._auto_repeat import AutoRepeatMixin
from ._bot_mangers import BotManagersMixin
from ._bttv_api import BetterTwitchTvApisMixin
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
                 FrankerFaceZApisMixin, BetterTwitchTvApisMixin):
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
        try:
            await self.open()
            return self
        except OSError:
            bot.globals.running = False
            raise

    async def __aexit__(self,
                        type: Optional[Type[BaseException]],
                        value: Optional[BaseException],
                        traceback: Optional[TracebackType]) -> None:
        await self.close()

    @staticmethod
    def datetimeToStr(dt: datetime) -> str:
        return f'{dt.isoformat()}Z'

    @staticmethod
    def strToDatetime(dt: Optional[str]) -> Optional[datetime]:
        if dt is None:
            return None
        isoFormat: str
        try:
            isoFormat = '%Y-%m-%dT%H:%M:%S.%fZ'
            return datetime.strptime(dt, isoFormat)
        except ValueError:
            pass
        isoFormat = '%Y-%m-%dT%H:%M:%SZ'
        return datetime.strptime(dt, isoFormat)
