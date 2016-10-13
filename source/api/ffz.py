import json
from http.client import HTTPResponse
from typing import Dict, Optional, Union
from urllib import request
from urllib.error import HTTPError, URLError

FfzEmoteDict = Dict[str, Union[int, str]]


def getGlobalEmotes() -> Optional[Dict[int, str]]:
    url = 'https://api.frankerfacez.com/v1/set/global'
    try:
        with request.urlopen(url) as response:
            if not isinstance(response, HTTPResponse):
                raise TypeError()
            if response.status == 200:
                responseData = response.read()  # type: bytes
                ffzData = json.loads(responseData.decode())  # type: dict
                emotes = {}  # type: Dict[int, str]
                for s in ffzData['default_sets']:  # type: str
                    for emote in ffzData['sets'][str(s)]['emoticons']:  # type: FfzEmoteDict
                        emotes[emote['id']] = emote['name']
                return emotes
    except HTTPError as e:
        if e.code == 404:
            return {}
    except URLError:
        pass
    return None


def getBroadcasterEmotes(broadcaster: str) -> Optional[Dict[int, str]]:
    url = 'https://api.frankerfacez.com/v1/room/' + broadcaster
    try:
        with request.urlopen(url) as response:
            if not isinstance(response, HTTPResponse):
                raise TypeError()
            if response.status == 200:
                responseData = response.read()  # type: bytes
                ffzData = json.loads(responseData.decode())  # type: dict
                emotes = {}
                ffzSet = ffzData['room']['set']  # type: str
                for emote in ffzData['sets'][str(ffzSet)]['emoticons']:  # type: FfzEmoteDict
                    emotes[emote['id']] = emote['name']
                return emotes
    except HTTPError as e:
        if e.code == 404:
            return {}
    except URLError:
        pass
    return None
