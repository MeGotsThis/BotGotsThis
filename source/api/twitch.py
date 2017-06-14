from bot import config
from source.api import oauth
from contextlib import closing, suppress
from datetime import datetime, timedelta
from http import client
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping
from typing import NamedTuple, Optional, Tuple, Union
import aiohttp
import asyncio
import bot.globals
import bot.utils
import configparser
import email.utils
import json
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


def client_id() -> Optional[str]:
    if os.path.isfile('twitchApi.ini'):
        ini = configparser.ConfigParser()
        ini.read('twitchApi.ini')
        if 'twitch' in ini and 'twitchClientID' in ini['twitch']:
            return ini['twitch']['twitchClientID']
    return None


def get_headers(headers: MutableMapping[str, str],
                channel: Optional[str]) -> MutableMapping[str, str]:
    if 'Accept' not in headers:
        headers['Accept'] = 'application/vnd.twitchtv.v5+json'
    if 'Client-ID' not in headers:
        clientId: Optional[str] = client_id()
        if clientId is not None:
            headers['Client-ID'] = clientId
    if channel is not None and 'Authorization' not in headers:
        token: Optional[str] = oauth.token(channel)
        if token is not None:
            headers['Authorization'] = 'OAuth ' + token
    return headers


def api_call(channel: Optional[str],
             method: str,
             uri: str,
             headers: MutableMapping[str, str]=None,
             data: Union[str, Mapping[str, str]]=None
             ) -> Tuple[client.HTTPResponse, bytes]:
    if headers is None:
        headers = {}
    headers = get_headers(headers, channel)
    connection: client.HTTPConnection
    connection = client.HTTPSConnection('api.twitch.tv')
    with closing(connection):
        dataStr: Optional[str] = None
        if data is not None:
            if isinstance(data, Mapping):
                dataStr = urllib.parse.urlencode(data)
            else:
                dataStr = data
        connection.request(method, uri, dataStr, headers)
        response: client.HTTPResponse
        with connection.getresponse() as response:
            return response, response.read()


async def get_call(channel: Optional[str],
                   uri: str,
                   headers: MutableMapping[str, str]=None
                   ) -> Tuple[Any, Optional[Dict]]:
    if headers is None:
        headers = {}
    headers = get_headers(headers, channel)
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.twitch.tv' + uri,
                               headers=headers,
                               timeout=config.httpTimeout) as response:
            try:
                return response, await response.json()
            except ValueError:
                return response, None


async def post_call(channel: Optional[str],
                    uri: str,
                    headers: MutableMapping[str, str]=None,
                    data: Union[str, Mapping[str, str]]=None
                    ) -> Tuple[aiohttp.ClientResponse, Optional[Dict]]:
    if headers is None:
        headers = {}
    headers = get_headers(headers, channel)
    dataStr: Optional[str] = None
    if data is not None:
        if isinstance(data, Mapping):
            dataStr = urllib.parse.urlencode(data)
        else:
            dataStr = data
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.twitch.tv' + uri,
                                headers=headers,
                                data=dataStr,
                                timeout=config.httpTimeout) as response:
            try:
                return response, await response.json()
            except ValueError:
                return response, None


async def put_call(channel: Optional[str],
                    uri: str,
                    headers: MutableMapping[str, str]=None,
                    data: Union[str, Mapping[str, str]]=None
                    ) -> Tuple[aiohttp.ClientResponse, Optional[Dict]]:
    if headers is None:
        headers = {}
    headers = get_headers(headers, channel)
    dataStr: Optional[str] = None
    if data is not None:
        if isinstance(data, Mapping):
            dataStr = urllib.parse.urlencode(data)
        else:
            dataStr = data
    async with aiohttp.ClientSession() as session:
        async with session.put('https://api.twitch.tv' + uri,
                               headers=headers,
                               data=dataStr,
                               timeout=config.httpTimeout) as response:
            try:
                return response, await response.json()
            except ValueError:
                return response, None


async def delete_call(channel: Optional[str],
                      uri: str,
                      headers: MutableMapping[str, str]=None,
                      data: Union[str, Mapping[str, str]]=None
                      ) -> Tuple[aiohttp.ClientResponse, Optional[Dict]]:
    if headers is None:
        headers = {}
    headers = get_headers(headers, channel)
    dataStr: Optional[str] = None
    if data is not None:
        if isinstance(data, Mapping):
            dataStr = urllib.parse.urlencode(data)
        else:
            dataStr = data
    async with aiohttp.ClientSession() as session:
        async with session.delete('https://api.twitch.tv' + uri,
                                  headers=headers,
                                  data=dataStr,
                                  timeout=config.httpTimeout) as response:
            return response, None


def server_time() -> Optional[datetime]:
    with suppress(client.HTTPException):
        response: client.HTTPResponse
        data: bytes
        response, data = api_call(None, 'GET', '/kraken/')
        if response.status == 200:
            date = response.getheader('Date')
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


def chat_server(chat:Optional[str]) -> Optional[str]:
    connection: client.HTTPConnection = client.HTTPSConnection('tmi.twitch.tv')
    with closing(connection):
        response: client.HTTPResponse
        data: bytes
        connection.request('GET', '/servers?channel=' + chat)
        with connection.getresponse() as response:
            responseData: bytes = response.read()
            with suppress(ValueError):
                jData: dict = json.loads(responseData.decode('utf-8'))
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


def is_valid_user(user: str) -> Optional[bool]:
    if not bot.utils.loadTwitchId(user):
        return None
    return bot.globals.twitchId[user] is not None


def num_followers(user: str) -> Optional[int]:
    if not bot.utils.loadTwitchId(user):
        return None
    if bot.globals.twitchId[user] is None:
        return 0
    with suppress(ConnectionError, client.HTTPException):
        response: client.HTTPResponse
        data: bytes
        uri: str = '/kraken/users/{}/follows/channels?limit=1'.format(
            bot.globals.twitchId[user])
        response, data = api_call(None, 'GET', uri)
        followerData: dict = json.loads(data.decode('utf-8'))
        return int(followerData['_total'])
    return None


def update(channel: str, *,
           status:Optional[str]=None,
           game:Optional[str]=None) -> Optional[bool]:
    if (not bot.utils.loadTwitchId(channel)
            or bot.globals.twitchId[channel] is None):
        return None
    postData: Dict[str, str] = {}
    if isinstance(status, str):
        postData['channel[status]'] = status or ' '
    if isinstance(game, str):
        postData['channel[game]'] = game
    if not postData:
        return None
    with suppress(ConnectionError, client.HTTPException):
        response: client.HTTPResponse
        data: bytes
        response, data = api_call(
            channel, 'PUT',
            '/kraken/channels/' + bot.globals.twitchId[channel],
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                },
            data=postData)
        return response.status == 200
    return None


async def active_streams(channels: Iterable[str]) -> Optional[OnlineStreams]:
    with suppress(aiohttp.ClientConnectionError, aiohttp.ClientResponseError,
                  asyncio.TimeoutError):
        allChannels: List[str] = [bot.globals.twitchId[c] for c in channels
                                  if bot.utils.loadTwitchId(c)
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
            time.sleep(0.05)
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


def channel_properties(channel: str) -> Optional[TwitchStatus]:
    if (not bot.utils.loadTwitchId(channel)
            or bot.globals.twitchId[channel] is None):
        return None
    uri: str = '/kraken/channels/' + bot.globals.twitchId[channel]
    with suppress(ConnectionError, client.HTTPException):
        response: client.HTTPResponse
        responseData: bytes
        response, responseData = api_call(None, 'GET', uri)
        if response.status != 200:
            return None
        channel_: Dict[str, str] = json.loads(responseData.decode('utf-8'))
        return TwitchStatus(None, channel_['status'], channel_['game'], None)
    return None


def channel_community(channel: str) -> Optional[TwitchCommunity]:
    if (not bot.utils.loadTwitchId(channel)
            or bot.globals.twitchId[channel] is None):
        return None
    uri: str = ('/kraken/channels/' + bot.globals.twitchId[channel]
                + '/community')
    with suppress(ConnectionError, client.HTTPException):
        response: client.HTTPResponse
        responseData: bytes
        response, responseData = api_call(None, 'GET', uri)
        if response.status == 204:
            return TwitchCommunity(None, None)
        if response.status != 200:
            return None
        community: Dict[str, str] = json.loads(responseData.decode('utf-8'))
        return TwitchCommunity(community['_id'], community['name'])
    return None


def get_community(communityName: str) -> Optional[TwitchCommunity]:
    uri: str = '/kraken/communities?name=' + urllib.parse.quote(communityName)
    with suppress(ConnectionError, client.HTTPException):
        response: client.HTTPResponse
        responseData: bytes
        response, responseData = api_call(None, 'GET', uri)
        if response.status != 200:
            return TwitchCommunity(None, None)
        community: Dict[str, str] = json.loads(responseData.decode('utf-8'))
        return TwitchCommunity(community['_id'], community['name'])
    return None


def get_community_by_id(communityId: str) -> Optional[TwitchCommunity]:
    uri: str = '/kraken/communities/' + communityId
    with suppress(ConnectionError, client.HTTPException):
        response: client.HTTPResponse
        responseData: bytes
        response, responseData = api_call(None, 'GET', uri)
        if response.status != 200:
            return TwitchCommunity(None, None)
        community: Dict[str, str] = json.loads(responseData.decode('utf-8'))
        return TwitchCommunity(community['_id'], community['name'])
    return None


def set_channel_community(channel: str,
                          communityName: Optional[str]) -> Optional[bool]:
    if (not bot.utils.loadTwitchId(channel)
            or bot.globals.twitchId[channel] is None):
        return None
    uri: str
    response: client.HTTPResponse
    responseData: bytes
    if communityName is not None:
        name: str = communityName.lower()
        if not bot.utils.loadTwitchCommunity(communityName):
            return None
        if bot.globals.twitchCommunity[name] is None:
            return False
        uri = ('/kraken/channels/' + bot.globals.twitchId[channel]
               + '/community/' + bot.globals.twitchCommunity[name])
        with suppress(ConnectionError, client.HTTPException):
            response, responseData = api_call(channel, 'PUT', uri)
            return True if response.status == 204 else None
    else:
        uri = ('/kraken/channels/' + bot.globals.twitchId[channel]
               + '/community')
        with suppress(ConnectionError, client.HTTPException):
            response, responseData = api_call(channel, 'DELETE', uri)
            return True if response.status == 204 else None
    return None
