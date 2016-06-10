import copy
import random
from bot import globals
from bot.data import channel
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ...api import bttv
from ...api import ffz
from ...api import twitch


def refreshTwitchGlobalEmotes(timestamp: datetime) -> None:
    if timestamp - globals.globalEmotesCache >= timedelta(hours=1):
        data = twitch.getTwitchEmotes()  # type: Optional[Tuple[Dict[int, str], Dict[int, int]]]
        if data:
            emotes, emoteSets = data
            globals.globalEmotesCache = timestamp
            globals.globalEmotes = emotes
            globals.globalEmoteSets = emoteSets


def refreshFrankerFaceZEmotes(timestamp: datetime) -> None:
    if timestamp - globals.globalFfzEmotesCache >= timedelta(hours=1):
        emotes = ffz.getGlobalEmotes()  # type: Optional[Dict[int, str]]
        if emotes:
            globals.globalFfzEmotesCache = timestamp
            globals.globalFfzEmotes = emotes
    channels = copy.copy(globals.channels)  # type: Dict[str, 'channel.Channel']
    toUpdate = [chan for chan in channels.values()
                if timestamp - chan.ffzCache >= timedelta(hours=1)
                and chan.streamingSince is not None]  # type: List['channel.Channel']
    if not toUpdate:
        toUpdate = [chan for chan in channels.values()
                    if timestamp - chan.ffzCache >= timedelta(hours=1)
                    and chan.streamingSince is None]
    if toUpdate:
        random.choice(toUpdate).updateFfzEmotes()


def refreshBetterTwitchTvEmotes(timestamp: datetime) -> None:
    if timestamp - globals.globalBttvEmotesCache >= timedelta(hours=1):
        emotes = bttv.getGlobalEmotes()
        if emotes:
            globals.globalBttvEmotesCache = timestamp
            globals.globalBttvEmotes = emotes
    channels = copy.copy(globals.channels)  # type: Dict[str, 'channel.Channel']
    toUpdate = [chan for chan in channels.values()
                if timestamp - chan.bttvCache >= timedelta(hours=1)
                and chan.streamingSince is not None]  # type: List['channel.Channel']
    if not toUpdate:
        toUpdate = [chan for chan in channels.values()
                    if timestamp - chan.bttvCache >= timedelta(hours=1)
                    and chan.streamingSince is None]
    if toUpdate:
        random.choice(toUpdate).updateBttvEmotes()
