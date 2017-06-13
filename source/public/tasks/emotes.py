import asyncio
import bot.globals
import copy
import random
from bot import data
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ...api import bttv
from ...api import ffz
from ...api import twitch


async def refreshTwitchGlobalEmotes(timestamp: datetime) -> None:
    if timestamp - bot.globals.globalEmotesCache >= timedelta(hours=1):
        bot.globals.globalEmotesCache = timestamp
        data: Optional[Tuple[Dict[int, str], Dict[int, int]]]
        data = await twitch.twitch_emotes()
        if data:
            emotes, emoteSets = data
            bot.globals.globalEmotes = emotes
            bot.globals.globalEmoteSets = emoteSets
        elif not bot.globals.globalEmotes:
            cache = timestamp - timedelta(hours=1) + timedelta(minutes=1)
            bot.globals.globalEmotesCache = cache
    else:
        await asyncio.sleep(0)


async def refreshFrankerFaceZEmotes(timestamp: datetime) -> None:
    await asyncio.wait([refreshFfzGlobalEmotes(timestamp),
                        refreshFfzRandomBroadcasterEmotes(timestamp)])


async def refreshFfzGlobalEmotes(timestamp: datetime) -> None:
    if timestamp - bot.globals.globalFfzEmotesCache >= timedelta(hours=1):
        emotes: Optional[Dict[int, str]]
        emotes = await ffz.getGlobalEmotes()
        bot.globals.globalFfzEmotesCache = timestamp
        if emotes is not None:
            bot.globals.globalFfzEmotes = emotes
    else:
        await asyncio.sleep(0)


async def refreshFfzRandomBroadcasterEmotes(timestamp: datetime) -> None:
    channels: Dict[str, data.Channel] = copy.copy(bot.globals.channels)
    toUpdate: List[data.Channel]
    toUpdate = [chan for chan in channels.values()
                if timestamp - chan.ffzCache >= timedelta(hours=1)
                and chan.isStreaming]
    if not toUpdate:
        toUpdate = [chan for chan in channels.values()
                    if timestamp - chan.ffzCache >= timedelta(hours=1)
                    and not chan.isStreaming]
    if toUpdate:
        await random.choice(toUpdate).updateFfzEmotes()
    else:
        await asyncio.sleep(0)


async def refreshBetterTwitchTvEmotes(timestamp: datetime) -> None:
    await asyncio.wait([refreshBttvGlobalEmotes(timestamp),
                        refreshBttvRandomBroadcasterEmotes(timestamp)])


async def refreshBttvGlobalEmotes(timestamp: datetime) -> None:
    if timestamp - bot.globals.globalBttvEmotesCache >= timedelta(hours=1):
        emotes: Optional[Dict[str, str]]
        emotes = await bttv.getGlobalEmotes()
        bot.globals.globalBttvEmotesCache = timestamp
        if emotes is not None:
            bot.globals.globalBttvEmotes = emotes
    else:
        await asyncio.sleep(0)


async def refreshBttvRandomBroadcasterEmotes(timestamp: datetime) -> None:
    channels: Dict[str, data.Channel] = copy.copy(bot.globals.channels)
    toUpdate: List[data.Channel]
    toUpdate = [chan for chan in channels.values()
                if timestamp - chan.bttvCache >= timedelta(hours=1)
                and chan.isStreaming]
    if not toUpdate:
        toUpdate = [chan for chan in channels.values()
                    if timestamp - chan.bttvCache >= timedelta(hours=1)
                    and not chan.isStreaming]
    if toUpdate:
        await random.choice(toUpdate).updateBttvEmotes()
    else:
        await asyncio.sleep(0)
