import asyncio
import datetime
import threading

from bot.async_task import background
from ..tasks import twitch


async def call_ids(timestamp: datetime.datetime) -> None:
    await twitch.checkTwitchIds(timestamp)


async def call_streams(timestamp: datetime.datetime) -> None:
    await twitch.checkStreamsAndChannel(timestamp)


async def call_offline(timestamp: datetime.datetime) -> None:
    await twitch.checkOfflineChannels(timestamp)


async def call_server(timestamp: datetime.datetime) -> None:
    await asyncio.sleep(0)
    twitch.checkChatServers(timestamp)


threading.Timer(1.5, background.add_task,
                [call_ids, datetime.timedelta(seconds=10)]).start()
threading.Timer(5, background.add_task,
                [call_streams, datetime.timedelta(seconds=30)]).start()
threading.Timer(10, background.add_task,
                [call_offline, datetime.timedelta(seconds=0.05)]).start()
threading.Timer(10, background.add_task,
                [call_server, datetime.timedelta(seconds=0.05)]).start()
