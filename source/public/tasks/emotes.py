from ...api import bttv
from ...api import ffz
from ...api import twitch
from bot import globals
import copy
import datetime
import random

def refreshTwitchGlobalEmotes(timestamp):
    since = timestamp - globals.globalEmotesCache
    if since >= datetime.timedelta(hours=1):
        twitch.updateTwitchEmotes()

def refreshFrankerFaceZEmotes(timestamp):
    cooldown = datetime.timedelta(hours=1)
    since = timestamp - globals.globalFfzEmotesCache
    if since >= cooldown:
        ffz.updateGlobalEmotes()
    channels = copy.copy(globals.channels)
    toUpdate = [channels[c] for c in globals.channels
                if timestamp - channels[c].ffzCache >= cooldown and
                channels[c].streamingSince is not None]
    if not toUpdate:
        toUpdate = [channels[c] for c in globals.channels
                    if timestamp - channels[c].ffzCache >= cooldown and
                    channels[c].streamingSince is None]
    if toUpdate:
        random.choice(toUpdate).updateFfzEmotes()

def refreshBetterTwitchTvEmotes(timestamp):
    cooldown = datetime.timedelta(hours=1)
    since = timestamp - globals.globalBttvEmotesCache
    if since >= cooldown:
        bttv.updateGlobalEmotes()
    channels = copy.copy(globals.channels)
    toUpdate = [channels[c] for c in globals.channels
                if timestamp - channels[c].bttvCache >= cooldown and
                channels[c].streamingSince is not None]
    if not toUpdate:
        toUpdate = [channels[c] for c in globals.channels
                    if timestamp - channels[c].bttvCache >= cooldown and
                    channels[c].streamingSince is None]
    if toUpdate:
        random.choice(toUpdate).updateBttvEmotes()
