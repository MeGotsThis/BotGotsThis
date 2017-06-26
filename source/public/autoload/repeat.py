﻿import datetime

from bot.coroutine import background
from ..tasks import repeat


async def call_autorepeat(timestamp: datetime.datetime) -> None:
    await repeat.autoRepeatMessage(timestamp)


background.add_task(call_autorepeat, datetime.timedelta(seconds=0.5))
