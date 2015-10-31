﻿from ...api import twitch
from bot import globals
import datetime

def refreshTwitchGlobalEmotes(timestamp):
    since = timestamp - globals.globalEmotesCache
    if since >= datetime.timedelta(hours=1):
        twitch.updateTwitchEmotes()

def refreshFrankerFaceZEmotes(timestamp):
    for chan in globals.channels:
        since = timestamp - globals.channels[chan].ffzCache
        if since >= datetime.timedelta(hours=1):
            globals.channels[chan].updateFfzEmotes()
            return
        