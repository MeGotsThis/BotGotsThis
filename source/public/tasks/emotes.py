import copy
import random
from bot import data, globals
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ...api import bttv
from ...api import ffz
from ...api import twitch


def refreshTwitchGlobalEmotes(timestamp: datetime) -> None:
    if timestamp - globals.globalEmotesCache >= timedelta(hours=1):
        data = twitch.twitch_emotes()  # type: Optional[Tuple[Dict[int, str], Dict[int, int]]]
        globals.globalEmotesCache = timestamp
        if data:
            emotes, emoteSets = data
            globals.globalEmotes = emotes
            globals.globalEmoteSets = emoteSets


def refreshFrankerFaceZEmotes(timestamp: datetime) -> None:
    refreshFfzGlobalEmotes(timestamp)
    refreshFfzRandomBroadcasterEmotes(timestamp)


def refreshFfzGlobalEmotes(timestamp: datetime) -> None:
    if timestamp - globals.globalFfzEmotesCache >= timedelta(hours=1):
        emotes = ffz.getGlobalEmotes()  # type: Optional[Dict[int, str]]
        globals.globalFfzEmotesCache = timestamp
        if emotes is not None:
            globals.globalFfzEmotes = emotes


def refreshFfzRandomBroadcasterEmotes(timestamp: datetime) -> None:
    channels = copy.copy(globals.channels)  # type: Dict[str, data.Channel]
    toUpdate = [chan for chan in channels.values()
                if timestamp - chan.ffzCache >= timedelta(hours=1)
                and chan.isStreaming]  # type: List[data.Channel]
    if not toUpdate:
        toUpdate = [chan for chan in channels.values()
                    if timestamp - chan.ffzCache >= timedelta(hours=1)
                    and not chan.isStreaming]
    if toUpdate:
        random.choice(toUpdate).updateFfzEmotes()


def refreshBetterTwitchTvEmotes(timestamp: datetime) -> None:
    refreshBttvGlobalEmotes(timestamp)
    refreshBttvRandomBroadcasterEmotes(timestamp)


def refreshBttvGlobalEmotes(timestamp: datetime) -> None:
    if timestamp - globals.globalBttvEmotesCache >= timedelta(hours=1):
        emotes = bttv.getGlobalEmotes()
        globals.globalBttvEmotesCache = timestamp
        if emotes is not None:
            globals.globalBttvEmotes = emotes


def refreshBttvRandomBroadcasterEmotes(timestamp: datetime) -> None:
    channels = copy.copy(globals.channels)  # type: Dict[str, data.Channel]
    toUpdate = [chan for chan in channels.values()
                if timestamp - chan.bttvCache >= timedelta(hours=1)
                and chan.isStreaming]  # type: List[data.Channel]
    if not toUpdate:
        toUpdate = [chan for chan in channels.values()
                    if timestamp - chan.bttvCache >= timedelta(hours=1)
                    and not chan.isStreaming]
    if toUpdate:
        random.choice(toUpdate).updateBttvEmotes()
