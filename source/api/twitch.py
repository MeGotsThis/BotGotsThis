from . import cache, oauth
from contextlib import closing, suppress
from datetime import datetime, timedelta
from http import client
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping
from typing import NamedTuple, Optional, Tuple, Union
import bot.globals
import bot.utils
import configparser
import email.utils
import json
import os.path
import time
import urllib.parse

DateTuple = Tuple[int, int, int, int, int, int, int, int, int]
TwitchStatus = NamedTuple('TwitchStatus',
                          [('streaming', Optional[datetime]),
                           ('status', Optional[str]),
                           ('game', Optional[str])])
TwitchEmotes = Dict[str, List[Dict[str, Union[str, int]]]]
OnlineStreams = Dict[str, TwitchStatus]


def client_id() -> Optional[str]:
    if os.path.isfile('twitchApi.ini'):
        ini = configparser.ConfigParser()
        ini.read('twitchApi.ini')
        if 'twitch' in ini and 'twitchClientID' in ini['twitch']:
            return ini['twitch']['twitchClientID']
    return None


def api_call(channel: Optional[str],
             method: str,
             uri: str,
             headers: MutableMapping[str, str]=None,
             data: Union[str, Mapping[str, str]]=None) -> Tuple[client.HTTPResponse, bytes]:
    if headers is None:
        headers = {}
    connection = client.HTTPSConnection('api.twitch.tv')  # type: client.HTTPConnection
    with closing(connection):
        if 'Accept' not in headers:
            headers['Accept'] = 'application/vnd.twitchtv.v5+json'
        if 'Client-ID' not in headers:
            clientId = client_id()  # type: Optional[str]
            if clientId is not None:
                headers['Client-ID'] = clientId
        if channel is not None and 'Authorization' not in headers:
            token = oauth.token(channel)  # type: Optional[str]
            if token is not None:
                headers['Authorization'] = 'OAuth ' + token
        dataStr = None  # type: Optional[str]
        if data is not None:
            if isinstance(data, Mapping):
                dataStr = urllib.parse.urlencode(data)
            else:
                dataStr = data
        connection.request(method, uri, dataStr, headers)
        with connection.getresponse() as response:  # type: client.HTTPResponse
            return response, response.read()


def server_time() -> Optional[datetime]:
    with suppress(client.HTTPException):
        response, data = api_call(None, 'GET', '/kraken/')  # type: client.HTTPResponse, bytes
        if response.status == 200:
            date = response.getheader('Date')
            if data is not None:
                dateStruct = email.utils.parsedate(date)  # type: DateTuple
                unixTimestamp = time.mktime(dateStruct)  # type: float
                return datetime.fromtimestamp(unixTimestamp)
    return None


def twitch_emotes() -> Optional[Tuple[Dict[int, str], Dict[int, int]]]:
    uri = ('/kraken/chat/emoticon_images?emotesets='
           + ','.join(str(i) for i in bot.globals.emoteset))  # type: str
    with suppress(ConnectionError, client.HTTPException):
        response, data = api_call(None, 'GET', uri)  # type: client.HTTPResponse, bytes
        globalEmotes = json.loads(data.decode('utf-8'))['emoticon_sets']  # type: TwitchEmotes
        emotes = {}  # type: Dict[int, str]
        emoteSet = {}  # type: Dict[int, int]
        replaceGlobal = {
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
            }  # type: Dict[int, str]
        for emoteSetId in globalEmotes:  # type: int
            for emote in globalEmotes[emoteSetId]:  # type: Dict[str, Union[str, int]
                id = int(emote['id'])  # type: int
                if id in replaceGlobal:
                    emotes[id] = replaceGlobal[id]
                else:
                    emotes[id] = str(emote['code'])
                emoteSet[id] = int(emoteSetId)
        return emotes, emoteSet
    return None


def chat_server(chat:Optional[str]) -> Optional[str]:
    connection = client.HTTPSConnection('tmi.twitch.tv')  # type: client.HTTPConnection
    with closing(connection):
        connection.request('GET', '/servers?channel=' + chat)
        with connection.getresponse() as response:  # type: client.HTTPResponse
            responseData = response.read()  # type: bytes
            with suppress(ValueError):
                jData = json.loads(responseData.decode('utf-8'))  # type: dict
                return str(jData['cluster'])
    return None


def getTwitchIds(channels: Iterable[str]) -> Optional[Dict[str, str]]:
    with suppress(ConnectionError, client.HTTPException):
        allChannels = list(channels)
        ids = {}  # type: Dict[str, str]
        for i in range((len(allChannels) + 99) // 100):
            channelsToCheck = allChannels[i*100:(i+1)*100]
            uri = '/kraken/users?limit=100&login=' + ','.join(channelsToCheck)  # type: str
            response, responseData = api_call(None, 'GET', uri)  # type: client.HTTPResponse, bytes
            if response.status != 200:
                return None
            idData = json.loads(responseData.decode('utf-8'))  # type: dict
            for userData in idData['users']:
                ids[userData['name']] = userData['_id']
        return ids
    return None


@cache('validTwitchUser', timedelta(minutes=1))
def is_valid_user(user: str) -> bool:
    user = user.lower()
    response, _ = api_call(
        None, 'GET', '/kraken/channels/' + user)  # type: client.HTTPResponse, bytes
    return response.status == 200


def num_followers(user: str) -> Optional[int]:
    if not bot.utils.loadTwitchId(user) or bot.globals.twitchId[user] is None:
        return None
    with suppress(ConnectionError, client.HTTPException):
        uri = '/kraken/users/{}/follows/channels?limit=1'.format(
            bot.globals.twitchId[user])  # type: str
        response, data = api_call(None, 'GET', uri)  # type: client.HTTPResponse, bytes
        followerData = json.loads(data.decode('utf-8'))  # type: dict
        return int(followerData['_total'])
    return None


def update(channel: str, *,
           status:Optional[str]=None,
           game:Optional[str]=None) -> Optional[bool]:
    if (not bot.utils.loadTwitchId(channel)
            or bot.globals.twitchId[channel] is None):
        return None
    postData = {}  # type: Dict[str, str]
    if isinstance(status, str):
        postData['channel[status]'] = status or ' '
    if isinstance(game, str):
        postData['channel[game]'] = game
    if not postData:
        return None
    with suppress(ConnectionError, client.HTTPException):
        response, data = api_call(
            channel, 'PUT',
            '/kraken/channels/' + bot.globals.twitchId[channel],
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                },
            data=postData)  # type: client.HTTPResponse, bytes
        return response.status == 200
    return None


def active_streams(channels: Iterable[str]) -> Optional[OnlineStreams]:
    with suppress(ConnectionError, client.HTTPException):
        allChannels = [c for c in channels
                       if bot.utils.loadTwitchId(c)
                       and bot.globals.twitchId[c] is not None]
        uri = '/kraken/streams?limit=100&channel=' + ','.join(allChannels)  # type: str
        response, responseData = api_call(None, 'GET', uri)  # type: client.HTTPResponse, bytes
        if response.status != 200:
            return None
        online = {}  # type: Dict[str, TwitchStatus]
        streamsData = json.loads(responseData.decode('utf-8'))  # type: dict
        _handle_streams(streamsData['streams'], online)
        for offset in range(100, streamsData['_total'], 100):
            time.sleep(0.05)
            offsetUri = uri + '&offset=' + offset  # type: str
            response, responseData = api_call(None, 'GET', offsetUri)
            if response.status != 200:
                break
            streamsData = json.loads(responseData.decode('utf-8'))
            _handle_streams(streamsData['streams'], online)
        return online
    return None


def _handle_streams(streams: List[Dict[str, Any]],
                    online: Dict[str, TwitchStatus]=None):
    if online is None:
        online = {}
    for stream in streams:  # type: Dict[str, Any]
        channel = stream['channel']['name'].lower()
        streamingSince = datetime.strptime(stream['created_at'],
                                           '%Y-%m-%dT%H:%M:%SZ')  # type: datetime
        online[channel] = TwitchStatus(
            streamingSince, stream['channel']['status'],
            stream['channel']['game'])
    return online


def channel_properties(channel: str) -> Optional[TwitchStatus]:
    if (not bot.utils.loadTwitchId(channel)
            or bot.globals.twitchId[channel] is None):
        return None
    uri = '/kraken/channels/' + bot.globals.twitchId[channel]  # type: str
    with suppress(ConnectionError, client.HTTPException):
        response, responseData = api_call(None, 'GET', uri)  # type: client.HTTPResponse, bytes
        if response.status != 200:
            return None
        channel_ = json.loads(responseData.decode('utf-8'))  # type: Dict[str, str]
        return TwitchStatus(None, channel_['status'], channel_['game'])
    return None
