import aiohttp

from typing import Dict, Optional

from bot import config


async def getGlobalEmotes() -> Optional[Dict[str, str]]:
    url: str = 'https://api.betterttv.net/2/emotes'
    response: aiohttp.ClientResponse
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url,
                                   timeout=config.httpTimeout) as response:
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


async def getBroadcasterEmotes(broadcaster: str) -> Optional[Dict[str, str]]:
    url: str = 'https://api.betterttv.net/2/channels/' + broadcaster
    response: aiohttp.ClientResponse
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url,
                                   timeout=config.httpTimeout) as response:
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
