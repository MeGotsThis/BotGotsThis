import datetime

from bot.coroutine import background
from . import tasks


async def call_autorepeat(timestamp: datetime.datetime) -> None:
    await tasks.autoRepeatMessage(timestamp)


background.add_task(call_autorepeat, datetime.timedelta(seconds=0.5))
