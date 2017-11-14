import asyncio
from typing import Set, Optional

import bot
from bot import data
from bot.twitchmessage import IrcMessageTagsReadOnly
from lib import cache

lock = asyncio.Lock()


def parse(channel: 'data.Channel',
          tags: Optional[IrcMessageTagsReadOnly]) -> None:
    if not isinstance(tags, IrcMessageTagsReadOnly):
        return
    bot.globals.displayName = str(tags['display-name'])
    bot.globals.isTwitchStaff = tags['user-type'] in ['staff']
    bot.globals.isTwitchAdmin = tags['user-type'] in ['staff', 'admin']
    bot.globals.isGlobalMod = tags['user-type'] in ['staff', 'admin',
                                                    'global_mod']
    if isinstance(channel, data.Channel):
        assert isinstance(tags['mod'], str)
        assert isinstance(tags['subscriber'], str)
        channel.isMod = bool(int(tags['mod'])) or bot.globals.isGlobalMod
        channel.isSubscriber = bool(int(tags['subscriber']))

    if 'emote-sets' in tags:
        emoteset: Set[int] = {int(i) for i
                              in str(tags['emote-sets']).split(',')}
        # This is to remove twitch turbo emotes that are shared with
        # global emoticons
        emoteset.discard(33)
        emoteset.discard(42)
        asyncio.ensure_future(handle_emote_set(emoteset))


async def handle_emote_set(emoteSet: Set[int]) -> None:
    if lock.locked():
        return
    async with lock:
        cacheStore: cache.CacheStore
        async with cache.get_cache() as cacheStore:
            await cacheStore.twitch_load_emotes(emoteSet, background=True)
