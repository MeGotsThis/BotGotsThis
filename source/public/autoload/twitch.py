from ..tasks import twitch
from bot.thread import background
import datetime

background.addTask(twitch.checkStreamsAndChannel,
                   datetime.timedelta(seconds=30))
