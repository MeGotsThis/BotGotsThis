from bot import globals
import datetime
import json
import urllib.request

def getGlobalEmotes():
    currentTime = datetime.datetime.utcnow()
    emotes = globals.globalBttvEmotes
    since = currentTime - globals.globalBttvEmotesCache
    url = 'https://api.betterttv.net/2/emotes'
    if since > datetime.timedelta(hours=1):
        globals.globalBttvEmotesCache = currentTime
        try:
            response = urllib.request.urlopen(url)
            if response.status == 200:
                responseData = response.read()
                bttvData = json.loads(responseData.decode())
                emotes = {}
                for emoteData in bttvData['emotes']:
                    emotes[emote['id']] = emote['code']
                globals.globalBttvEmotes = emotes
        except:
            pass
    return emotes

def getBroadcasterEmotes(broadcaster):
    url = 'https://api.betterttv.net/2/channels/' + broadcaster
    try:
        response = urllib.request.urlopen(url)
        if response.status == 200:
            responseData = response.read()
            bttvData = json.loads(responseData.decode())
            emotes = {}
            for emoteData in bttvData['emotes']:
                emotes[emote['id']] = emote['code']
            return emotes
    except:
        pass
    return None
