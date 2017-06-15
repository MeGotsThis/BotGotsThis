import datetime

from bot.coroutine import background
from ..tasks import emotes


async def call_twitch(timestamp: datetime.datetime) -> None:
    await emotes.refreshTwitchGlobalEmotes(timestamp)


async def call_ffz(timestamp: datetime.datetime) -> None:
    await emotes.refreshFrankerFaceZEmotes(timestamp)


async def call_bttv(timestamp: datetime.datetime) -> None:
     await emotes.refreshBetterTwitchTvEmotes(timestamp)


background.add_task(call_twitch, datetime.timedelta(seconds=1))
background.add_task(call_ffz, datetime.timedelta(milliseconds=.75))
background.add_task(call_bttv, datetime.timedelta(milliseconds=.75))
