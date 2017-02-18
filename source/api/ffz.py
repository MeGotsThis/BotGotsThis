import json
from http.client import HTTPResponse
from typing import BinaryIO, Dict, Optional, Union
from urllib import request
from urllib.error import HTTPError, URLError


def getGlobalEmotes() -> Optional[Dict[int, str]]:
    url: str = 'https://api.frankerfacez.com/v1/set/global'
    response: Union[HTTPResponse, BinaryIO]
    try:
        with request.urlopen(url) as response:
            if not isinstance(response, HTTPResponse):
                raise TypeError()
            if response.status == 200:
                responseData: bytes = response.read()
                ffzData: dict = json.loads(responseData.decode())
                emotes: Dict[int, str] = {}
                emote: dict
                s: str
                for s in ffzData['default_sets']:
                    for emote in ffzData['sets'][str(s)]['emoticons']:
                        emotes[emote['id']] = emote['name']
                return emotes
    except HTTPError as e:
        if e.code == 404:
            return {}
    except URLError:
        pass
    return None


def getBroadcasterEmotes(broadcaster: str) -> Optional[Dict[int, str]]:
    url: str = 'https://api.frankerfacez.com/v1/room/' + broadcaster
    response: Union[HTTPResponse, BinaryIO]
    try:
        with request.urlopen(url) as response:
            if not isinstance(response, HTTPResponse):
                raise TypeError()
            if response.status == 200:
                responseData: bytes = response.read()
                ffzData: dict = json.loads(responseData.decode())
                emotes: Dict[int, str] = {}
                ffzSet: str = ffzData['room']['set']
                emote: dict
                for emote in ffzData['sets'][str(ffzSet)]['emoticons']:
                    emotes[emote['id']] = emote['name']
                return emotes
    except HTTPError as e:
        if e.code == 404:
            return {}
    except URLError:
        pass
    return None
