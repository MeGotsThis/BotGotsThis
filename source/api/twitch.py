from source.api import oauth
from contextlib import closing, suppress
from datetime import datetime, timedelta
from http import client
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping
from typing import NamedTuple, Optional, Tuple, Union
import aiohttp
import asyncio
import bot
import bot.globals
import bot.utils
import configparser
import email.utils
import os.path
import time
import urllib.parse

DateTuple = Tuple[int, int, int, int, int, int, int, int, int]
TwitchEmotes = Dict[str, List[Dict[str, Union[str, int]]]]


class TwitchStatus(NamedTuple):
    streaming: Optional[datetime]
    status: Optional[str]
    game: Optional[str]
    communityId: Optional[str]

OnlineStreams = Dict[str, TwitchStatus]


class TwitchCommunity(NamedTuple):
    id: Optional[str]
    name: Optional[str]


async def get_headers(headers: MutableMapping[str, str],
                      channel: Optional[str]) -> MutableMapping[str, str]:
    if 'Accept' not in headers:
        headers['Accept'] = 'application/vnd.twitchtv.v5+json'
    if 'Client-ID' not in headers:
        clientId: Optional[str] = bot.config.twitchClientId
        if clientId is not None:
            headers['Client-ID'] = clientId
    if channel is not None and 'Authorization' not in headers:
        token: Optional[str] = await oauth.token(channel)
        if token is not None:
            headers['Authorization'] = 'OAuth ' + token
    return headers


async def get_call(channel: Optional[str],
                   uri: str,
                   headers: MutableMapping[str, str]=None
                   ) -> Tuple[Any, Optional[Dict]]:
    if headers is None:
        headers = {}
    headers = await get_headers(headers, channel)
    async with aiohttp.ClientSession(raise_for_status=True) as session, \
            session.get('https://api.twitch.tv' + uri,
                        headers=headers,
                        timeout=bot.config.httpTimeout) as response:
        if response.status == 204:
            return response, None
        try:
            return response, await response.json()
        except aiohttp.ClientResponseError:
            return response, None


async def post_call(channel: Optional[str],
                    uri: str,
                    headers: MutableMapping[str, str]=None,
                    data: Union[str, Mapping[str, str]]=None
                    ) -> Tuple[aiohttp.ClientResponse, Optional[Dict]]:
    if headers is None:
        headers = {}
    headers = await get_headers(headers, channel)
    dataStr: Optional[str] = None
    if data is not None:
        if isinstance(data, Mapping):
            dataStr = urllib.parse.urlencode(data)
        else:
            dataStr = data
    async with aiohttp.ClientSession(raise_for_status=True) as session, \
            session.post('https://api.twitch.tv' + uri,
                         headers=headers,
                         data=dataStr,
                         timeout=bot.config.httpTimeout) as response:
        if response.status == 204:
            return response, None
        try:
            return response, await response.json()
        except aiohttp.ClientResponseError:
            return response, None


async def put_call(channel: Optional[str],
                    uri: str,
                    headers: MutableMapping[str, str]=None,
                    data: Union[str, Mapping[str, str]]=None
                    ) -> Tuple[aiohttp.ClientResponse, Optional[Dict]]:
    if headers is None:
        headers = {}
    headers = await get_headers(headers, channel)
    dataStr: Optional[str] = None
    if data is not None:
        if isinstance(data, Mapping):
            dataStr = urllib.parse.urlencode(data)
        else:
            dataStr = data
    async with aiohttp.ClientSession(raise_for_status=True) as session, \
            session.put('https://api.twitch.tv' + uri,
                        headers=headers,
                        data=dataStr,
                        timeout=bot.config.httpTimeout) as response:
        if response.status == 204:
            return response, None
        try:
            return response, await response.json()
        except aiohttp.ClientResponseError:
            return response, None


async def delete_call(channel: Optional[str],
                      uri: str,
                      headers: MutableMapping[str, str]=None,
                      data: Union[str, Mapping[str, str]]=None
                      ) -> Tuple[aiohttp.ClientResponse, Optional[Dict]]:
    if headers is None:
        headers = {}
    headers = await get_headers(headers, channel)
    dataStr: Optional[str] = None
    if data is not None:
        if isinstance(data, Mapping):
            dataStr = urllib.parse.urlencode(data)
        else:
            dataStr = data
    async with aiohttp.ClientSession(raise_for_status=True) as session, \
            session.delete('https://api.twitch.tv' + uri,
                           headers=headers,
                           data=dataStr,
                           timeout=bot.config.httpTimeout) as response:
        if response.status == 204:
            return response, None
        try:
            return response, await response.json()
        except aiohttp.ClientResponseError:
            return response, None


async def server_time() -> Optional[datetime]:
    with suppress(aiohttp.ClientConnectionError, aiohttp.ClientResponseError,
                  asyncio.TimeoutError):
        response: aiohttp.ClientResponse
        data: dict
        response, data = await get_call(None, '/kraken/')
        if response.status == 200:
            date = response.headers['Date']
            if data is not None:
                dateStruct: DateTuple = email.utils.parsedate(date)
                unixTimestamp: float = time.mktime(dateStruct)
                return datetime.fromtimestamp(unixTimestamp)
    return None


async def twitch_emotes() -> Optional[Tuple[Dict[int, str], Dict[int, int]]]:
    uri: str = ('/kraken/chat/emoticon_images?emotesets='
                + ','.join(str(i) for i in bot.globals.emoteset))
    with suppress(aiohttp.ClientConnectionError, aiohttp.ClientResponseError,
                  asyncio.TimeoutError):
        response: aiohttp.ClientResponse
        data: Optional[Dict]
        globalEmotes: TwitchEmotes
        response, data = await get_call(None, uri)
        if data is None:
            return None
        globalEmotes = data['emoticon_sets']
        emotes: Dict[int, str] = {}
        emoteSet: Dict[int, int] = {}
        replaceGlobal: Dict[int, str] = {
            1: ':)',
            2: ':(',
            3: ':D',
            4: '>(',
            5: ':z',
            6: 'o_O',
            7: 'B)',
            8: ':o',
            9: '<3',
            10: ':\\',
            11: ';)',
            12: ':P',
            13: ';P',
            14: 'R)',
            }
        emoteSetId: str
        emote: Dict[str, Union[str, int]]
        for emoteSetId in globalEmotes:
            for emote in globalEmotes[emoteSetId]:
                id: int = int(emote['id'])
                if id in replaceGlobal:
                    emotes[id] = replaceGlobal[id]
                else:
                    emotes[id] = str(emote['code'])
                emoteSet[id] = int(emoteSetId)
        return emotes, emoteSet
    return None


async def chat_server(chat: str) -> Optional[str]:
    session: aiohttp.ClientSession
    response: aiohttp.ClientResponse
    async with aiohttp.ClientSession() as session, \
            session.get('https://tmi.twitch.tv/servers?channel=' + chat,
                        timeout=bot.config.httpTimeout) as response:
        with suppress(ValueError, aiohttp.ClientResponseError):
            jData: dict = await response.json()
            return str(jData['cluster'])
    return None


async def getTwitchIds(channels: Iterable[str]) -> Optional[Dict[str, str]]:
    with suppress(aiohttp.ClientConnectionError, aiohttp.ClientResponseError,
                  asyncio.TimeoutError):
        allChannels: List[str] = list(channels)
        ids: Dict[str, str] = {}
        for i in range((len(allChannels) + 99) // 100):
            channelsToCheck: List[str] = allChannels[i*100:(i+1)*100]
            uri: str
            uri = '/kraken/users?limit=100&login=' + ','.join(channelsToCheck)
            response: aiohttp.ClientResponse
            idData: Optional[dict]
            response, idData = await get_call(None, uri)
            if response.status != 200 or idData is None:
                return None
            for userData in idData['users']:
                ids[userData['name']] = userData['_id']
        return ids
    return None


async def is_valid_user(user: str) -> Optional[bool]:
    if not await bot.utils.loadTwitchId(user):
        return None
    return bot.globals.twitchId[user] is not None


async def num_followers(user: str) -> Optional[int]:
    if not await bot.utils.loadTwitchId(user):
        return None
    if bot.globals.twitchId[user] is None:
        return 0
    with suppress(aiohttp.ClientConnectionError, aiohttp.ClientResponseError,
                  asyncio.TimeoutError):
        response: client.HTTPResponse
        followerData: dict
        uri: str = '/kraken/users/{}/follows/channels?limit=1'.format(
            bot.globals.twitchId[user])
        response, followerData = await get_call(None, uri)
        return int(followerData['_total'])
    return None


async def update(channel: str, *,
                 status: Optional[str]=None,
                 game: Optional[str]=None) -> Optional[bool]:
    if (not await bot.utils.loadTwitchId(channel)
            or bot.globals.twitchId[channel] is None):
        return None
    postData: Dict[str, str] = {}
    if isinstance(status, str):
        postData['channel[status]'] = status or ' '
    if isinstance(game, str):
        postData['channel[game]'] = game
    if not postData:
        return None
    with suppress(aiohttp.ClientConnectionError, aiohttp.ClientResponseError,
                  asyncio.TimeoutError):
        response: aiohttp.ClientResponse
        data: Optional[dict]
        response, data = await put_call(
            channel, '/kraken/channels/' + bot.globals.twitchId[channel],
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=postData)
        return response.status == 200
    return None


async def active_streams(channels: Iterable[str]) -> Optional[OnlineStreams]:
    with suppress(aiohttp.ClientConnectionError, aiohttp.ClientResponseError,
                  asyncio.TimeoutError):
        allChannels: List[str] = [bot.globals.twitchId[c] for c in channels
                                  if await bot.utils.loadTwitchId(c)
                                  and bot.globals.twitchId[c] is not None]
        if not allChannels:
            return {}
        uri: str = '/kraken/streams?limit=100&channel=' + ','.join(allChannels)
        response: aiohttp.ClientResponse
        streamsData: dict
        response, streamsData = await get_call(None, uri)
        if response.status != 200:
            return None
        online: Dict[str, TwitchStatus] = {}
        _handle_streams(streamsData['streams'], online)
        for offset in range(100, streamsData['_total'], 100):
            await asyncio.sleep(0.05)
            offsetUri: str = uri + '&offset=' + str(offset)
            response, streamsData = await get_call(None, offsetUri)
            if response.status != 200:
                break
            _handle_streams(streamsData['streams'], online)
        return online
    return None


def _handle_streams(streams: List[Dict[str, Any]],
                    online: Dict[str, TwitchStatus]=None):
    if online is None:
        online = {}
    stream: Dict[str, Any]
    for stream in streams:
        channel = stream['channel']['name'].lower()
        streamingSince: datetime = datetime.strptime(stream['created_at'],
                                                     '%Y-%m-%dT%H:%M:%SZ')
        online[channel] = TwitchStatus(
            streamingSince, stream['channel']['status'],
            stream['channel']['game'],
            stream['community_id'] or None)
    return online


async def channel_properties(channel: str) -> Optional[TwitchStatus]:
    if (not await bot.utils.loadTwitchId(channel)
            or bot.globals.twitchId[channel] is None):
        return None
    uri: str = '/kraken/channels/' + bot.globals.twitchId[channel]
    with suppress(aiohttp.ClientConnectionError, aiohttp.ClientResponseError,
                  asyncio.TimeoutError):
        response: aiohttp.ClientResponse
        channel_: Optional[Dict[str, str]]
        response, channel_ = await get_call(None, uri)
        if response.status != 200:
            return None
        return TwitchStatus(None, channel_['status'], channel_['game'], None)
    return None


async def channel_community(channel: str) -> Optional[TwitchCommunity]:
    if (not await bot.utils.loadTwitchId(channel)
            or bot.globals.twitchId[channel] is None):
        return None
    uri: str = ('/kraken/channels/' + bot.globals.twitchId[channel]
                + '/community')
    with suppress(ConnectionError, client.HTTPException):
        response: client.HTTPResponse
        community: Optional[Dict[str, str]]
        response, community = await get_call(None, uri)
        if response.status not in [200, 204]:
            return None
        if community is None:
            return TwitchCommunity(None, None)
        return TwitchCommunity(community['_id'], community['name'])
    return None


async def get_community(communityName: str) -> Optional[TwitchCommunity]:
    uri: str = '/kraken/communities?name=' + urllib.parse.quote(communityName)
    with suppress(aiohttp.ClientConnectionError, aiohttp.ClientResponseError,
                  asyncio.TimeoutError):
        response: aiohttp.ClientResponse
        community: Optional[Dict[str, str]]
        response, community = await get_call(None, uri)
        if response.status != 200:
            return TwitchCommunity(None, None)
        return TwitchCommunity(community['_id'], community['name'])
    return None


async def get_community_by_id(communityId: str) -> Optional[TwitchCommunity]:
    uri: str = '/kraken/communities/' + communityId
    with suppress(aiohttp.ClientConnectionError, aiohttp.ClientResponseError,
                  asyncio.TimeoutError):
        response: aiohttp.ClientResponse
        community: Optional[Dict[str, str]]
        response, community = await get_call(None, uri)
        if response.status != 200:
            return TwitchCommunity(None, None)
        return TwitchCommunity(community['_id'], community['name'])
    return None


async def set_channel_community(channel: str,
                                communityName: Optional[str]
                                ) -> Optional[bool]:
    if (not await bot.utils.loadTwitchId(channel)
            or bot.globals.twitchId[channel] is None):
        return None
    uri: str
    response: aiohttp.ClientResponse
    data: Optional[dict]
    if communityName is not None:
        name: str = communityName.lower()
        if not await bot.utils.loadTwitchCommunity(communityName):
            return None
        if bot.globals.twitchCommunity[name] is None:
            return False
        uri = ('/kraken/channels/' + bot.globals.twitchId[channel]
               + '/community/' + bot.globals.twitchCommunity[name])
        with suppress(aiohttp.ClientConnectionError,
                      aiohttp.ClientResponseError,
                      asyncio.TimeoutError):
            response, data = await put_call(channel, uri)
            return True if response.status == 204 else None
    else:
        uri = ('/kraken/channels/' + bot.globals.twitchId[channel]
               + '/community')
        with suppress(aiohttp.ClientConnectionError,
                      aiohttp.ClientResponseError,
                      asyncio.TimeoutError):
            response, data = await delete_call(channel, uri)
            return True if response.status == 204 else None
    return None
