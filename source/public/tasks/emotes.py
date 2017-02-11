import bot.globals
import copy
import random
from bot import data
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ...api import bttv
from ...api import ffz
from ...api import twitch


def refreshTwitchGlobalEmotes(timestamp: datetime) -> None:
    if timestamp - bot.globals.globalEmotesCache >= timedelta(hours=1):
        oldTimestamp = bot.globals.globalEmotesCache  # type: datetime
        bot.globals.globalEmotesCache = timestamp
        data = twitch.twitch_emotes()  # type: Optional[Tuple[Dict[int, str], Dict[int, int]]]
        if data:
            emotes, emoteSets = data
            bot.globals.globalEmotes = emotes
            bot.globals.globalEmoteSets = emoteSets
        elif not bot.globals.globalEmotes:
            bot.globals.globalEmotesCache = oldTimestamp + timedelta(minutes=1)


def refreshFrankerFaceZEmotes(timestamp: datetime) -> None:
    refreshFfzGlobalEmotes(timestamp)
    refreshFfzRandomBroadcasterEmotes(timestamp)


def refreshFfzGlobalEmotes(timestamp: datetime) -> None:
    if timestamp - bot.globals.globalFfzEmotesCache >= timedelta(hours=1):
        emotes = ffz.getGlobalEmotes()  # type: Optional[Dict[int, str]]
        bot.globals.globalFfzEmotesCache = timestamp
        if emotes is not None:
            bot.globals.globalFfzEmotes = emotes


def refreshFfzRandomBroadcasterEmotes(timestamp: datetime) -> None:
    channels = copy.copy(bot.globals.channels)  # type: Dict[str, data.Channel]
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
    if timestamp - bot.globals.globalBttvEmotesCache >= timedelta(hours=1):
        emotes = bttv.getGlobalEmotes()
        bot.globals.globalBttvEmotesCache = timestamp
        if emotes is not None:
            bot.globals.globalBttvEmotes = emotes


def refreshBttvRandomBroadcasterEmotes(timestamp: datetime) -> None:
    channels = copy.copy(bot.globals.channels)  # type: Dict[str, data.Channel]
    toUpdate = [chan for chan in channels.values()
                if timestamp - chan.bttvCache >= timedelta(hours=1)
                and chan.isStreaming]  # type: List[data.Channel]
    if not toUpdate:
        toUpdate = [chan for chan in channels.values()
                    if timestamp - chan.bttvCache >= timedelta(hours=1)
                    and not chan.isStreaming]
    if toUpdate:
        random.choice(toUpdate).updateBttvEmotes()
