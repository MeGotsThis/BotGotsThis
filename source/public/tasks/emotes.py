import datetime
import ircbot.irc
import ircbot.twitchApi

def refreshTwitchGlobalEmotes(timestamp):
    since = timestamp - ircbot.irc.globalEmotesCache
    if since >= datetime.timedelta(hours=1):
        ircbot.twitchApi.updateTwitchEmotes()

def refreshFrankerFaceZEmotes(timestamp):
    for chan in ircbot.irc.channels:
        since = timestamp - ircbot.irc.channels[chan].ffzCache
        if since >= datetime.timedelta(hours=1):
            ircbot.irc.channels[chan].updateFfzEmotes()
            return
        