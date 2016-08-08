from ..tasks import emotes
from bot.globals import background
import datetime


def call_twitch(timestamp: datetime.datetime) -> None:
    emotes.refreshTwitchGlobalEmotes(timestamp)


def call_ffz(timestamp: datetime.datetime) -> None:
    emotes.refreshFrankerFaceZEmotes(timestamp)


def call_bttv(timestamp: datetime.datetime) -> None:
    emotes.refreshBetterTwitchTvEmotes(timestamp)


background.addTask(call_twitch, datetime.timedelta(seconds=1))
background.addTask(call_ffz, datetime.timedelta(milliseconds=.75))
background.addTask(call_bttv, datetime.timedelta(milliseconds=.75))
