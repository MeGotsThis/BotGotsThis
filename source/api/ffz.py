from bot import globals
from contextlib import suppress
import datetime
import json
import urllib.request

def updateGlobalEmotes():
    globals.globalFfzEmotesCache = datetime.datetime.utcnow()
    url = 'https://api.frankerfacez.com/v1/set/global'
    with suppress(urllib.request.URLError):
        response = urllib.request.urlopen(url)
        if response.status == 200:
            responseData = response.read()
            ffzData = json.loads(responseData.decode())
            emotes = {}
            for s in ffzData['default_sets']:
                for emote in ffzData['sets'][str(s)]['emoticons']:
                    emotes[emote['id']] = emote['name']
            globals.globalFfzEmotes = emotes

def getBroadcasterEmotes(broadcaster):
    url = 'https://api.frankerfacez.com/v1/room/' + broadcaster
    with suppress(urllib.request.URLError):
        response = urllib.request.urlopen(url)
        if response.status == 200:
            responseData = response.read()
            ffzData = json.loads(responseData.decode())
            emotes = {}
            ffzSet = ffzData['room']['set']
            for emote in ffzData['sets'][str(ffzSet)]['emoticons']:
                emotes[emote['id']] = emote['name']
            return emotes
    return None
