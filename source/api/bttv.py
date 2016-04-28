from bot import globals
import datetime
import json
import urllib.request

def updateGlobalEmotes():
    globals.globalBttvEmotesCache = datetime.datetime.utcnow()
    url = 'https://api.betterttv.net/2/emotes'
    try:
        response = urllib.request.urlopen(url)
        if response.status == 200:
            responseData = response.read()
            bttvData = json.loads(responseData.decode())
            emotes = {}
            for emote in bttvData['emotes']:
                emotes[emote['id']] = emote['code']
            globals.globalBttvEmotes = emotes
    except:
        pass

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
