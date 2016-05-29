from ..tasks import emotes
from bot.globals import background
import datetime

background.addTask(emotes.refreshTwitchGlobalEmotes,
                   datetime.timedelta(seconds=1))
background.addTask(emotes.refreshFrankerFaceZEmotes,
                   datetime.timedelta(milliseconds=.75))
background.addTask(emotes.refreshBetterTwitchTvEmotes,
                   datetime.timedelta(milliseconds=.75))
