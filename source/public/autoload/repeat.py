from ..tasks import repeat
from bot.globals import background
import datetime


def call_autorepeat(timestamp: datetime.datetime) -> None:
    repeat.autoRepeatMessage(timestamp)


background.addTask(call_autorepeat, datetime.timedelta(seconds=0.5))
