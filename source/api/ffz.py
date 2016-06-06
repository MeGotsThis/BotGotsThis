import json
import urllib.request
from contextlib import suppress


def getGlobalEmotes():
    url = 'https://api.frankerfacez.com/v1/set/global'
    with suppress(urllib.request.URLError), \
            urllib.request.urlopen(url) as response:
        if response.status == 200:
            responseData = response.read()
            ffzData = json.loads(responseData.decode())
            emotes = {}
            for s in ffzData['default_sets']:
                for emote in ffzData['sets'][str(s)]['emoticons']:
                    emotes[emote['id']] = emote['name']
            return emotes
    return None


def getBroadcasterEmotes(broadcaster):
    url = 'https://api.frankerfacez.com/v1/room/' + broadcaster
    with suppress(urllib.request.URLError), \
            urllib.request.urlopen(url) as response:
        if response.status == 200:
            responseData = response.read()
            ffzData = json.loads(responseData.decode())
            emotes = {}
            ffzSet = ffzData['room']['set']
            for emote in ffzData['sets'][str(ffzSet)]['emoticons']:
                emotes[emote['id']] = emote['name']
            return emotes
    return None
