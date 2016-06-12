import json
from http.client import HTTPResponse
from contextlib import suppress
from typing import Dict, Optional, Union
from urllib.error import URLError
from urllib.request import urlopen

FfzEmoteDict = Dict[str, Union[int, str]]


def getGlobalEmotes() -> Optional[Dict[int, str]]:
    url = 'https://api.frankerfacez.com/v1/set/global'
    with suppress(URLError), urlopen(url) as response:
        if not isinstance(response, HTTPResponse):
            raise TypeError()
        if response.status == 200:
            responseData = response.read()  # type: bytes
            ffzData = json.loads(responseData.decode())  # type: dict
            emotes = {}  # type: Dict[int, str]
            for s in ffzData['default_sets']:  # --type: str
                for emote in ffzData['sets'][str(s)]['emoticons']:  # --type: FfzEmoteDict
                    emotes[emote['id']] = emote['name']
            return emotes
    return None


def getBroadcasterEmotes(broadcaster: str) -> Optional[Dict[int, str]]:
    url = 'https://api.frankerfacez.com/v1/room/' + broadcaster
    with suppress(URLError), urlopen(url) as response:
        if not isinstance(response, HTTPResponse):
            raise TypeError()
        if response.status == 200:
            responseData = response.read()  # type: bytes
            ffzData = json.loads(responseData.decode())  # type: dict
            emotes = {}
            ffzSet = ffzData['room']['set']  # type: str
            for emote in ffzData['sets'][str(ffzSet)]['emoticons']:  # --type: FfzEmoteDict
                emotes[emote['id']] = emote['name']
            return emotes
    return None
