import copy
import random
from datetime import timedelta

from bot import globals
from ...api import bttv
from ...api import ffz
from ...api import twitch


def refreshTwitchGlobalEmotes(timestamp):
    if timestamp - globals.globalEmotesCache >= timedelta(hours=1):
        data = twitch.getTwitchEmotes()
        if data:
            emotes, emoteSets = data
            globals.globalEmotesCache = timestamp
            globals.globalEmotes = emotes
            globals.globalEmoteSets = emoteSets


def refreshFrankerFaceZEmotes(timestamp):
    if timestamp - globals.globalFfzEmotesCache >= timedelta(hours=1):
        emotes = ffz.getGlobalEmotes()
        if emotes:
            globals.globalFfzEmotesCache = timestamp
            globals.globalFfzEmotes = emotes
    channels = copy.copy(globals.channels)
    toUpdate = [chan for chan in channels.values()
                if timestamp - chan.ffzCache >= timedelta(hours=1)
                and chan.streamingSince is not None]
    if not toUpdate:
        toUpdate = [chan for chan in channels.values()
                    if timestamp - chan.ffzCache >= timedelta(hours=1)
                    and chan.streamingSince is None]
    if toUpdate:
        random.choice(toUpdate).updateFfzEmotes()


def refreshBetterTwitchTvEmotes(timestamp):
    if timestamp - globals.globalBttvEmotesCache >= timedelta(hours=1):
        emotes = bttv.getGlobalEmotes()
        if emotes:
            globals.globalBttvEmotesCache = timestamp
            globals.globalBttvEmotes = emotes
    channels = copy.copy(globals.channels)
    toUpdate = [chan for chan in channels.values()
                if timestamp - chan.bttvCache >= timedelta(hours=1)
                and chan.streamingSince is not None]
    if not toUpdate:
        toUpdate = [chan for chan in channels.values()
                    if timestamp - chan.bttvCache >= timedelta(hours=1)
                    and chan.streamingSince is None]
    if toUpdate:
        random.choice(toUpdate).updateBttvEmotes()
