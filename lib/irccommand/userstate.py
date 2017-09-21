from bot import data
from bot.twitchmessage import IrcMessageTagsReadOnly
from typing import List, Optional  # noqa: F401
import datetime
import bot


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

    emoteset: List[int] = [int(i) for i in str(tags['emote-sets']).split(',')]
    # This is to remove twitch turbo emotes that are shared with
    # global emoticons
    if 33 in emoteset:
        emoteset.remove(33)
    if 42 in emoteset:
        emoteset.remove(42)
    if bot.globals.emoteset != emoteset:
        bot.globals.emoteset = emoteset
        bot.globals.globalEmotesCache = datetime.datetime.min
