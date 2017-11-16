import asyncio
import datetime

from bot.coroutine import background
from ..tasks import twitch


async def call_ids(timestamp: datetime.datetime) -> None:
    await twitch.checkTwitchIds(timestamp)


async def call_streams(timestamp: datetime.datetime) -> None:
    await twitch.checkStreamsAndChannel(timestamp)


async def call_offline(timestamp: datetime.datetime) -> None:
    await twitch.checkOfflineChannels(timestamp)


loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
loop.call_later(1.5, background.add_task, call_ids,
                datetime.timedelta(seconds=10))
loop.call_later(5, background.add_task, call_streams,
                datetime.timedelta(seconds=30))
loop.call_later(10, background.add_task, call_offline,
                datetime.timedelta(seconds=0.05))
