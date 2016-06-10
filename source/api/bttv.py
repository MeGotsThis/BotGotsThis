import json
import urllib.request
from contextlib import suppress
from http.client import HTTPResponse
from typing import Dict, Optional


def getGlobalEmotes() -> Optional[Dict[str, str]]:
    url = 'https://api.betterttv.net/2/emotes'
    with suppress(urllib.request.URLError), urllib.request.urlopen(url) as response:  # type: ignore
        if not isinstance(response, HTTPResponse):
            raise TypeError()
        if response.status == 200:
            responseData = response.read()  # type: bytes
            bttvData = json.loads(responseData.decode())  # type: Dict[str, List[Dict[str, str]]]
            emotes = {}  # type: Dict[str, str]
            for emote in bttvData['emotes']:  # --type: Dict[str, str]
                emotes[emote['id']] = emote['code']
            return emotes
    return None


def getBroadcasterEmotes(broadcaster: str) -> Optional[Dict[str, str]]:
    url = 'https://api.betterttv.net/2/channels/' + broadcaster
    with suppress(urllib.request.URLError), urllib.request.urlopen(url) as response:  # type: ignore
        if not isinstance(response, HTTPResponse):
            raise TypeError()
        if response.status == 200:
            responseData = response.read()  # type: bytes
            bttvData = json.loads(responseData.decode())  # type: Dict[str, List[Dict[str, str]]]
            emotes = {}  # type: Dict[str, str]
            for emote in bttvData['emotes']:  # --type: Dict[str, str]
                emotes[emote['id']] = emote['code']
            return emotes
    return None
