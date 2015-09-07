import datetime
import ircbot.irc
import ircbot.twitchApi

def refreshTwitchGlobalEmotes(timestamp):
    since = timestamp - ircbot.irc.globalEmotesCache
    if since >= datetime.timedelta(hours=1):
        ircbot.twitchApi.getTwitchEmotes()

def refreshFrankerFaceZEmotes(timestamp):
    for channel in ircbot.irc.channels:
        since = timestamp - channel.ffzCache
        if since >= datetime.timedelta(hours=1):
            channel.ffzEmotes
            return
        