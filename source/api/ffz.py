import asyncio

import aiohttp

from typing import Dict, Optional

from bot import config


async def getGlobalEmotes() -> Optional[Dict[int, str]]:
    url: str = 'https://api.frankerfacez.com/v1/set/global'
    response: aiohttp.ClientResponse
    try:
        async with aiohttp.ClientSession(raise_for_status=True) as session, \
                session.get(url, timeout=config.httpTimeout) as response:
            if response.status != 200:
                return None
            ffzData: dict = await response.json()
            emotes: Dict[int, str] = {}
            emote: dict
            s: str
            for s in ffzData['default_sets']:
                for emote in ffzData['sets'][str(s)]['emoticons']:
                    emotes[emote['id']] = emote['name']
            return emotes
    except aiohttp.ClientResponseError as e:
        if e.code == 404:
            return {}
    except asyncio.TimeoutError:
        pass
    return None


async def getBroadcasterEmotes(broadcaster: str) -> Optional[Dict[int, str]]:
    url: str = 'https://api.frankerfacez.com/v1/room/' + broadcaster
    response: aiohttp.ClientResponse
    try:
        async with aiohttp.ClientSession(raise_for_status=True) as session, \
                session.get(url, timeout=config.httpTimeout) as response:
            if response.status != 200:
                return None
            ffzData: dict = await response.json()
            emotes: Dict[int, str] = {}
            ffzSet: str = ffzData['room']['set']
            emote: dict
            for emote in ffzData['sets'][str(ffzSet)]['emoticons']:
                emotes[emote['id']] = emote['name']
            return emotes
    except aiohttp.ClientResponseError as e:
        if e.code == 404:
            return {}
    except asyncio.TimeoutError:
        pass
    return None
