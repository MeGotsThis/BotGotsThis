from lib.api import oauth
from contextlib import suppress
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping
from typing import NamedTuple, Optional, Set, Tuple, Union  # noqa: F401
import aiohttp
import asyncio
import bot
import bot.utils
import email.utils
import json
import time
import urllib.parse

JsonData = Any
DateStruct = Optional[Tuple[int, int, int, int, int, int, int, int, int]]
TwitchEmotes = Dict[str, List[Dict[str, Union[str, int]]]]


class TwitchStatus(NamedTuple):
    streaming: Optional[datetime]
    status: Optional[str]
    game: Optional[str]
    communityId: List[str]


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
                   ) -> Tuple[aiohttp.ClientResponse, JsonData]:
    if headers is None:
        headers = {}
    headers = await get_headers(headers, channel)
    response: aiohttp.ClientResponse
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
                    ) -> Tuple[aiohttp.ClientResponse, JsonData]:
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
                   ) -> Tuple[aiohttp.ClientResponse, JsonData]:
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
                      ) -> Tuple[aiohttp.ClientResponse, JsonData]:
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
        data: Dict[str, Any]
        response, data = await get_call(None, '/kraken/')
        if response.status != 200:
            return None
        if 'Date' not in response.headers:
            return None
        date = response.headers['Date']
        dateStruct: DateStruct = email.utils.parsedate(date)
        if dateStruct is None:
            return None
        unixTimestamp: float = time.mktime(dateStruct)
        return datetime.fromtimestamp(unixTimestamp)
    return None


async def twitch_emotes() -> Optional[Tuple[Dict[int, str], Dict[int, int]]]:
    uri: str = ('/kraken/chat/emoticon_images?emotesets='
                + ','.join(str(i) for i in bot.globals.emoteset))
    with suppress(aiohttp.ClientConnectionError, aiohttp.ClientResponseError,
                  asyncio.TimeoutError):
        response: aiohttp.ClientResponse
        data: Optional[Dict[str, Any]]
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
                assert isinstance(emote['id'], int)
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
            jData: Dict[str, Any] = await response.json()
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
            idData: Optional[Dict[str, Any]]
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
        response: aiohttp.ClientResponse
        followerData: Dict[str, Any]
        twitchId: str = bot.globals.twitchId[user]
        uri: str = f'/kraken/users/{twitchId}/follows/channels?limit=1'
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
        data: Optional[Dict[str, Any]]
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
        streamsData: Dict[str, Any]
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
                    online: Dict[str, TwitchStatus]=None
                    ) -> Dict[str, TwitchStatus]:
    if online is None:
        online = {}
    stream: Dict[str, Any]
    for stream in streams:
        channel = stream['channel']['name'].lower()
        streamingSince: datetime = datetime.strptime(stream['created_at'],
                                                     '%Y-%m-%dT%H:%M:%SZ')
        online[channel] = TwitchStatus(
            streamingSince, stream['channel']['status'],
            stream['channel']['game'], stream['community_ids'])
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
        return TwitchStatus(None, channel_['status'], channel_['game'], [])
    return None


async def channel_community(channel: str) -> Optional[List[TwitchCommunity]]:
    if (not await bot.utils.loadTwitchId(channel)
            or bot.globals.twitchId[channel] is None):
        return None
    uri: str = f'/kraken/channels/{bot.globals.twitchId[channel]}/communities'
    with suppress(ConnectionError, aiohttp.ClientResponseError):
        response: aiohttp.ClientResponse
        communities: Optional[Dict[str, List[Dict[str, str]]]]
        response, communities = await get_call(None, uri)
        if response.status not in [200, 204]:
            return None
        if communities is None:
            return []
        chanCommunities: List[TwitchCommunity] = []
        community: Dict[str, str]
        for community in communities['communities']:
            chanCommunities.append(
                TwitchCommunity(community['_id'], community['name']))
        return chanCommunities
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
                                communities: List[str]
                                ) -> Optional[List[str]]:
    if (not await bot.utils.loadTwitchId(channel)
            or bot.globals.twitchId[channel] is None):
        return None
    uri: str
    response: aiohttp.ClientResponse
    data: Optional[Dict[str, Any]]
    if communities:
        communityIds: Set[str] = set()
        for communityName in communities:
            name: str = communityName.lower()
            if not await bot.utils.loadTwitchCommunity(communityName):
                return None
            if bot.globals.twitchCommunity[name] is None:
                continue
            communityIds.add(bot.globals.twitchCommunity[name])
        if not communityIds:
            return []
        uri = f'/kraken/channels/{bot.globals.twitchId[channel]}/communities'
        data = {'community_ids': list(communityIds)}
        headers: Dict[str, str] = {'Content-Type': 'application/json'}
        with suppress(aiohttp.ClientConnectionError,
                      aiohttp.ClientResponseError,
                      asyncio.TimeoutError):
            response, data = await put_call(channel, uri,
                                            headers=headers,
                                            data=json.dumps(data))
            return list(communityIds) if response.status == 204 else None
    else:
        uri = f'/kraken/channels/{bot.globals.twitchId[channel]}/community'
        with suppress(aiohttp.ClientConnectionError,
                      aiohttp.ClientResponseError,
                      asyncio.TimeoutError):
            response, data = await delete_call(channel, uri)
            return [] if response.status == 204 else None
    return None
