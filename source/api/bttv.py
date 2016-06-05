from bot import globals
from contextlib import suppress
import json
import urllib.request

def getGlobalEmotes():
    url = 'https://api.betterttv.net/2/emotes'
    with suppress(urllib.request.URLError):
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                responseData = response.read()
                bttvData = json.loads(responseData.decode())
                emotes = {}
                for emote in bttvData['emotes']:
                    emotes[emote['id']] = emote['code']
                return emotes
    return None

def getBroadcasterEmotes(broadcaster):
    url = 'https://api.betterttv.net/2/channels/' + broadcaster
    with suppress(urllib.request.URLError):
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                responseData = response.read()
                bttvData = json.loads(responseData.decode())
                emotes = {}
                for emoteData in bttvData['emotes']:
                    emotes[emote['id']] = emote['code']
                return emotes
    return None
