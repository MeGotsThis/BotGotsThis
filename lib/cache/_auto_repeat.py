import json
from datetime import datetime, timedelta
from typing import AsyncIterator, List, Optional  # noqa: F401

from bot import utils
from ._abc import AbcCacheStore
from .. import data, database


class AutoRepeatMixin(AbcCacheStore):
    async def loadAutoRepeats(self) -> 'List[data.RepeatData]':
        repeats: List[data.RepeatData]
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            repeats = [r async for r in db.getAutoRepeats()]
        await self.redis.setex(
            'autorepeat', 600,
            json.dumps([repeat[:-1] + (repeat.last.isoformat() + 'Z',)
                        for repeat in repeats]))
        return repeats

    async def _getAutoRepeats(self) -> 'List[data.RepeatData]':
        value: Optional[str] = await self.redis.get('autorepeat')
        if value is None:
            return await self.loadAutoRepeats()
        else:
            isoFormat: str = '%Y-%m-%dT%H:%M:%S.%fZ'
            return [
                data.RepeatData(
                    repeat[0], repeat[1], repeat[2], repeat[3], repeat[4],
                    datetime.strptime(repeat[5], isoFormat))
                for repeat in json.loads(value)]

    async def getAutoRepeatToSend(self, timestamp: Optional[datetime]=None
                                  ) -> 'AsyncIterator[data.AutoRepeatMessage]':
        now: datetime = timestamp or utils.now()
        repeats: List[data.RepeatData] = await self._getAutoRepeats()
        repeat: data.RepeatData
        for repeat in repeats:
            if repeat.last + timedelta(minutes=repeat.duration) > now:
                continue
            yield data.AutoRepeatMessage(repeat.broadcaster, repeat.name,
                                         repeat.message)

    async def listAutoRepeat(self, broadcaster: str
                             ) -> 'AsyncIterator[data.AutoRepeatList]':
        repeats: List[data.RepeatData] = await self._getAutoRepeats()
        repeat: data.RepeatData
        for repeat in repeats:
            if repeat.broadcaster != broadcaster:
                continue
            yield data.AutoRepeatList(
                repeat.name, repeat.message, repeat.remaining, repeat.duration,
                repeat.last)

    async def resetAutoRepeats(self) -> None:
        await self.redis.delete('autorepeat')

    async def clearAutoRepeat(self, broadcaster: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.clearAutoRepeat(broadcaster)
        if val:
            await self.resetAutoRepeats()
        return val

    async def sentAutoRepeat(self,
                             broadcaster: str,
                             name: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.sentAutoRepeat(broadcaster, name)
        if val:
            await self.resetAutoRepeats()
        return val

    async def setAutoRepeat(self,
                            broadcaster: str,
                            name: str,
                            message: str,
                            count: Optional[int],
                            minutes: float) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.setAutoRepeat(broadcaster, name, message, count,
                                         minutes)
        if val:
            await self.resetAutoRepeats()
        return val

    async def removeAutoRepeat(self,
                               broadcaster: str,
                               name: str) -> bool:
        val: bool
        db: database.DatabaseMain
        async with database.get_main_database() as db:
            val = await db.removeAutoRepeat(broadcaster, name)
        if val:
            await self.resetAutoRepeats()
        return val
