import json
from http.client import HTTPResponse
from typing import Dict, Optional
from urllib import request
from urllib.error import HTTPError, URLError


def getGlobalEmotes() -> Optional[Dict[str, str]]:
    url = 'https://api.betterttv.net/2/emotes'
    try:
        with request.urlopen(url) as response:
            if not isinstance(response, HTTPResponse):
                raise TypeError()
            if response.status == 200:
                responseData = response.read()  # type: bytes
                bttvData = json.loads(responseData.decode())  # type: dict
                emotes = {}  # type: Dict[str, str]
                for emote in bttvData['emotes']:  # type: Dict[str, str]
                    emotes[emote['id']] = emote['code']
                return emotes
    except HTTPError as e:
        if e.code == 404:
            return {}
    except URLError:
        pass
    return None


def getBroadcasterEmotes(broadcaster: str) -> Optional[Dict[str, str]]:
    url = 'https://api.betterttv.net/2/channels/' + broadcaster
    try:
        with request.urlopen(url) as response:
            if not isinstance(response, HTTPResponse):
                raise TypeError()
            if response.status == 200:
                responseData = response.read()  # type: bytes
                bttvData = json.loads(responseData.decode())  # type: dict
                emotes = {}  # type: Dict[str, str]
                for emote in bttvData['emotes']:  # type: Dict[str, str]
                    emotes[emote['id']] = emote['code']
                return emotes
    except HTTPError as e:
        if e.code == 404:
            return {}
    except URLError:
        pass
    return None
