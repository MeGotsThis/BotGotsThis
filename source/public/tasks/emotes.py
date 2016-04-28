from ...api import bttv
from ...api import ffz
from ...api import twitch
from bot import globals
import datetime

def refreshTwitchGlobalEmotes(timestamp):
    since = timestamp - globals.globalEmotesCache
    if since >= datetime.timedelta(hours=1):
        twitch.updateTwitchEmotes()

def refreshFrankerFaceZEmotes(timestamp):
    since = timestamp - globals.globalFfzEmotesCache
    if since >= datetime.timedelta(hours=1):
        ffz.updateGlobalEmotes()
    for chan in globals.channels:
        since = timestamp - globals.channels[chan].ffzCache
        if since >= datetime.timedelta(hours=1):
            globals.channels[chan].updateFfzEmotes()
            return

def refreshBetterTwitchTvEmotes(timestamp):
    for chan in globals.channels:
        since = timestamp - globals.channels[chan].bttvCache
        if since >= datetime.timedelta(hours=1):
            globals.channels[chan].updateBttvEmotes()
            return
