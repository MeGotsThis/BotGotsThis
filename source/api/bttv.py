import aiohttp
import json
from http.client import HTTPResponse
from typing import BinaryIO, Dict, Optional, Union
from urllib import request
from urllib.error import HTTPError, URLError


async def getGlobalEmotes() -> Optional[Dict[str, str]]:
    url: str = 'https://api.betterttv.net/2/emotes'
    response: aiohttp.ClientResponse
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                bttvData: dict = await response.json()
                emotes: Dict[str, str] = {}
                emote: Dict[str, str]
                for emote in bttvData['emotes']:
                    emotes[emote['id']] = emote['code']
                return emotes
    except aiohttp.ClientResponseError as e:
        if e.code == 404:
            return {}
    return None


def getBroadcasterEmotes(broadcaster: str) -> Optional[Dict[str, str]]:
    url: str = 'https://api.betterttv.net/2/channels/' + broadcaster
    response: Union[HTTPResponse, BinaryIO]
    try:
        with request.urlopen(url) as response:
            if not isinstance(response, HTTPResponse):
                raise TypeError()
            if response.status == 200:
                responseData: bytes = response.read()
                bttvData: dict = json.loads(responseData.decode())
                emotes: Dict[str, str] = {}
                emote: Dict[str, str]
                for emote in bttvData['emotes']:
                    emotes[emote['id']] = emote['code']
                return emotes
    except HTTPError as e:
        if e.code == 404:
            return {}
    except URLError:
        pass
    return None
