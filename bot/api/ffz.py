from .. import globals
import datetime
import json
import urllib.request

def getGlobalEmotes():
    currentTime = datetime.datetime.utcnow()
    emotes = ircbot.irc.globalFfzEmotes
    since = currentTime - ircbot.irc.globalFfzEmotesCache
    url = 'https://api.frankerfacez.com/v1/set/global'
    if since > datetime.timedelta(hours=1):
        ircbot.irc.globalFfzEmotesCache = currentTime
        try:
            response = urllib.request.urlopen(url)
            if response.status == 200:
                responseData = response.read()
                ffzData = json.loads(responseData.decode())
                emotes = {}
                for s in ffzData['default_sets']:
                    for emote in ffzData['sets'][str(s)]['emoticons']:
                        emotes[emote['id']] = emote['name']
                ircbot.irc.globalFfzEmotes = emotes
        except:
            pass
    return emotes

def getBroadcasterEmotes(broadcaster):
    url = 'https://api.frankerfacez.com/v1/room/' + broadcaster
    try:
        response = urllib.request.urlopen(url)
        if response.status == 200:
            responseData = response.read()
            ffzData = json.loads(responseData.decode())
            emotes = {}
            ffzSet = ffzData['room']['set']
            for emote in ffzData['sets'][str(ffzSet)]['emoticons']:
                emotes[emote['id']] = emote['name']
            return emotes
    except:
        pass
    return None
