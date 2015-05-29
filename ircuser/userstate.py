import datetime
import ircbot.irc

def parse(channelData, tags):
    ircbot.irc.displayName = tags['display-name']
    ircbot.irc.isTwitchStaff = tags['user-type'] in ['staff']
    ircbot.irc.isTwitchAdmin = tags['user-type'] in ['staff', 'admin']
    ircbot.irc.isTwitchTurbo = bool(int(tags['turbo']))
    channelData.isMod = tags['user-type'] in ['staff', 'admin', 'mod']
    
    emoteset = tags['emotesets'].split(',')
    emoteset = [int(i) for i in emoteset]
    # This is to remove twitch turbo emotes that are shared with
    # global emoticons
    if 33 in emoteset:
        emoteset.remove(33)
    if 42 in emoteset:
        emoteset.remove(42)
    if ircbot.irc.emoteset != emoteset:
        ircbot.irc.emoteset = emoteset
        ircbot.irc.globalEmotesCache = datetime.datetime.min
