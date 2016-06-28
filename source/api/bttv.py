import json
from http.client import HTTPResponse
from typing import Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def getGlobalEmotes() -> Optional[Dict[str, str]]:
    url = 'https://api.betterttv.net/2/emotes'
    try:
        with urlopen(url) as response:
            if not isinstance(response, HTTPResponse):
                raise TypeError()
            if response.status == 200:
                responseData = response.read()  # type: bytes
                bttvData = json.loads(responseData.decode())  # type: dict
                emotes = {}  # type: Dict[str, str]
                for emote in bttvData['emotes']:  # --type: Dict[str, str]
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
        with urlopen(url) as response:
            if not isinstance(response, HTTPResponse):
                raise TypeError()
            if response.status == 200:
                responseData = response.read()  # type: bytes
                bttvData = json.loads(responseData.decode())  # type: dict
                emotes = {}  # type: Dict[str, str]
                for emote in bttvData['emotes']:  # --type: Dict[str, str]
                    emotes[emote['id']] = emote['code']
                return emotes
    except HTTPError as e:
        if e.code == 404:
            return {}
    except URLError:
        pass
    return None
