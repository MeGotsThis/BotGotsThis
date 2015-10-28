import datetime
import bot.globals

def parse(channelData, tags):
    bot.globals.displayName = tags['display-name']
    bot.globals.isTwitchStaff = tags['user-type'] in ['staff']
    bot.globals.isTwitchAdmin = tags['user-type'] in ['staff', 'admin']
    bot.globals.isTwitchTurbo = bool(int(tags['turbo']))
    channelData.isMod = tags['user-type'] in ['staff', 'admin', 'mod']
    
    emoteset = tags['emote-sets'].split(',')
    emoteset = [int(i) for i in emoteset]
    # This is to remove twitch turbo emotes that are shared with
    # global emoticons
    if 33 in emoteset:
        emoteset.remove(33)
    if 42 in emoteset:
        emoteset.remove(42)
    if bot.globals.emoteset != emoteset:
        bot.globals.emoteset = emoteset
        bot.globals.globalEmotesCache = datetime.datetime.min
