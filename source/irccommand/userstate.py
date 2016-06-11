from bot import data
from bot.twitchmessage.irctags import IrcMessageTagsReadOnly
from typing import List
import datetime
import bot.globals


def parse(channel: 'data.Channel',
          tags: IrcMessageTagsReadOnly) -> None:
    bot.globals.displayName = str(tags['display-name'])
    bot.globals.isTwitchStaff = tags['user-type'] in ['staff']
    bot.globals.isTwitchAdmin = tags['user-type'] in ['staff', 'admin']
    bot.globals.isTwitchTurbo = bool(int(tags['turbo']))
    channel.isMod = tags['user-type'] in ['staff', 'admin', 'mod']
    
    emoteset = [int(i) for i in str(tags['emote-sets']).split(',')]  # List[int]
    # This is to remove twitch turbo emotes that are shared with
    # global emoticons
    if 33 in emoteset:
        emoteset.remove(33)
    if 42 in emoteset:
        emoteset.remove(42)
    if bot.globals.emoteset != emoteset:
        bot.globals.emoteset = emoteset
        bot.globals.globalEmotesCache = datetime.datetime.min
