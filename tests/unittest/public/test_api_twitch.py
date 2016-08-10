import bot.globals
import json
import unittest
from collections import defaultdict
from datetime import datetime
from http.client import HTTPException, HTTPResponse
from source.api import twitch
from tests.unittest.mock_class import StrContains, TypeMatch
from unittest.mock import MagicMock, Mock, patch

chatServers = b'''{
    "cluster": "aws",
    "servers": [
        "irc.chat.twitch.tv:6667",
        "irc.chat.twitch.tv:80"
    ],
    "websockets_servers": [
        "irc-ws.chat.twitch.tv:80"
    ]
}'''

twitchEmotes = b'''{
    "emoticon_sets": {
        "0": [
            {
                "id": 25,
                "code": "Kappa"
            }
        ]
    }
}'''

twitchEmotesSpecial = br'''{
    "emoticon_sets": {
        "0": [
            {
                "id": 7,
                "code": "B-?\\)"
            },
            {
                "id": 5,
                "code": "\\:-?[z|Z|\\|]"
            },
            {
                "id": 1,
                "code": "\\:-?\\)"
            },
            {
                "id": 2,
                "code": "\\:-?\\("
            },
            {
                "id": 12,
                "code": "\\:-?(p|P)"
            },
            {
                "id": 13,
                "code": "\\;-?(p|P)"
            },
            {
                "id": 9,
                "code": "\\&lt\\;3"
            },
            {
                "id": 11,
                "code": "\\;-?\\)"
            },
            {
                "id": 14,
                "code": "R-?\\)"
            },
            {
                "id": 3,
                "code": "\\:-?D"
            },
            {
                "id": 8,
                "code": "\\:-?(o|O)"
            },
            {
                "id": 4,
                "code": "\\&gt\\;\\("
            }
        ]
    }
}'''

numFollowers = b'''{
    "follows": [
        {
            "created_at": "2000-01-01T00:00:00Z",
            "_links": {
                "self": "https://api.twitch.tv/kraken/users/botgotsthis/follows/channels/megotsthis"
            },
            "notifications": true,
            "channel": {
            }
        }
    ],
    "_total": 1,
    "_links": {
        "self": "https://api.twitch.tv/kraken/users/botgotsthis/follows/channels?direction=DESC&limit=25&offset=0&sortby=created_at",
        "next": "https://api.twitch.tv/kraken/users/botgotsthis/follows/channels?direction=DESC&limit=25&offset=25&sortby=created_at"
    }
}'''

noStreams = b'''{
    "streams": [
    ],
    "_total": 1,
    "_links": {
        "self": "https://api.twitch.tv/kraken/streams?channel=thetyrant14\\u0026limit=100\\u0026offset=0",
        "next": "https://api.twitch.tv/kraken/streams?channel=thetyrant14\\u0026limit=100\\u0026offset=100",
        "featured": "https://api.twitch.tv/kraken/streams/featured",
        "summary": "https://api.twitch.tv/kraken/streams/summary",
        "followed": "https://api.twitch.tv/kraken/streams/followed"
    }
}'''

multiStreams = b'''{
    "streams": [
        1
    ],
    "_total": 101,
    "_links": {
        "self": "https://api.twitch.tv/kraken/streams?channel=thetyrant14\\u0026limit=100\\u0026offset=0",
        "next": "https://api.twitch.tv/kraken/streams?channel=thetyrant14\\u0026limit=100\\u0026offset=100",
        "featured": "https://api.twitch.tv/kraken/streams/featured",
        "summary": "https://api.twitch.tv/kraken/streams/summary",
        "followed": "https://api.twitch.tv/kraken/streams/followed"
    }
}'''

streams = '''[
    {
        "_id": 1,
        "game": null,
        "viewers": 9000,
        "created_at": "2000-01-01T00:00:00Z",
        "video_height": 2160,
        "average_fps": 59.94,
        "delay": 0,
        "is_playlist": false,
        "_links": {
            "self": "https://api.twitch.tv/kraken/streams/botgotsthis"
        },
        "preview": {
            "small": "https://static-cdn.jtvnw.net/previews-ttv/live_user_botgotsthis-80x45.jpg",
            "medium": "https://static-cdn.jtvnw.net/previews-ttv/live_user_botgotsthis-320x180.jpg",
            "large": "https://static-cdn.jtvnw.net/previews-ttv/live_user_botgotsthis-640x360.jpg",
            "template": "https://static-cdn.jtvnw.net/previews-ttv/live_user_botgotsthis-{width}x{height}.jpg"
        },
        "channel": {
            "mature": false,
            "status": null,
            "broadcaster_language": "en",
            "display_name": "BotGotsThis",
            "game": null,
            "language": "en",
            "_id": 1,
            "name": "botgotsthis",
            "created_at": "2000-01-01T00:00:00Z",
            "updated_at": "2000-01-01T00:00:00Z",
            "delay": null,
            "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/botgotsthis-profile_image-604f9ed5ada9dad7-300x300.png",
            "banner": null,
            "video_banner": "https://static-cdn.jtvnw.net/jtv_user_pictures/botgotsthis-channel_offline_image-91a5f5054b756233-1920x1080.png",
            "background": null,
            "profile_banner": "https://static-cdn.jtvnw.net/jtv_user_pictures/botgotsthis-profile_banner-4d4e3ec4abc918d7-480.png",
            "profile_banner_background_color": "#ffffff",
            "partner": false,
            "url": "https://www.twitch.tv/botgotsthis",
            "views": 0,
            "followers": 0,
            "_links": {
                "self": "http://api.twitch.tv/kraken/channels/botgotsthis",
                "follows": "http://api.twitch.tv/kraken/channels/botgotsthis/follows",
                "commercial": "http://api.twitch.tv/kraken/channels/botgotsthis/commercial",
                "stream_key": "http://api.twitch.tv/kraken/channels/botgotsthis/stream_key",
                "chat": "http://api.twitch.tv/kraken/chat/botgotsthis",
                "features": "http://api.twitch.tv/kraken/channels/botgotsthis/features",
                "subscriptions": "http://api.twitch.tv/kraken/channels/botgotsthis/subscriptions",
                "editors": "http://api.twitch.tv/kraken/channels/botgotsthis/editors",
                "teams": "http://api.twitch.tv/kraken/channels/botgotsthis/teams",
                "videos": "http://api.twitch.tv/kraken/channels/botgotsthis/videos"
            }
        }
    }
]'''

channelProperties = b'''{
    "mature": false,
    "status": null,
    "broadcaster_language": "en",
    "display_name": "BotGotsThis",
    "game": null,
    "language": "en",
    "_id": 1,
    "name": "megotsthis",
    "created_at": "2000-01-01T00:00:00Z",
    "updated_at": "2000-01-01T00:00:00Z",
    "delay": null,
    "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/botgotsthis-profile_image-fd1cf7913c217e92-300x300.png",
    "banner": null,
    "video_banner": null,
    "background": null,
    "profile_banner": null,
    "profile_banner_background_color": null,
    "partner": false,
    "url": "https://www.twitch.tv/botgotsthis",
    "views": 1,
    "followers": 1,
    "_links": {
        "self": "https://api.twitch.tv/kraken/channels/botgotsthis",
        "follows": "https://api.twitch.tv/kraken/channels/botgotsthis/follows",
        "commercial": "https://api.twitch.tv/kraken/channels/botgotsthis/commercial",
        "stream_key": "https://api.twitch.tv/kraken/channels/botgotsthis/stream_key",
        "chat": "https://api.twitch.tv/kraken/chat/botgotsthis",
        "features": "https://api.twitch.tv/kraken/channels/botgotsthis/features",
        "subscriptions": "https://api.twitch.tv/kraken/channels/botgotsthis/subscriptions",
        "editors": "https://api.twitch.tv/kraken/channels/botgotsthis/editors",
        "teams": "https://api.twitch.tv/kraken/channels/botgotsthis/teams",
        "videos": "https://api.twitch.tv/kraken/channels/botgotsthis/videos"
    }
}'''


class TestApiTwitchApiCalls(unittest.TestCase):
    def setUp(self):
        patcher = patch('source.api.twitch.client_id')
        self.addCleanup(patcher.stop)
        self.mock_clientid = patcher.start()
        self.mock_clientid.return_value = '0123456789abcdef'

        patcher = patch('http.client.HTTPSConnection', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_httpconnection = patcher.start()

        patcher = patch('source.api.oauth.token', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_token = patcher.start()
        self.mock_token.return_value = 'abcdef0123456789'

    def test_api_call(self):
        twitch.api_call('botgotsthis', 'GET', '/kraken/',
                        data={'bot': 'BotGotsThis'})
        self.assertTrue(self.mock_clientid.called)
        self.assertTrue(self.mock_token.called)

    def test_api_call_channel_none(self):
        twitch.api_call(None, 'GET', '/kraken/', data={'bot': 'BotGotsThis'})
        self.assertTrue(self.mock_clientid.called)
        self.assertFalse(self.mock_token.called)

    def test_api_call_data_none(self):
        twitch.api_call(None, 'GET', '/kraken/')
        self.assertTrue(self.mock_clientid.called)
        self.assertFalse(self.mock_token.called)

    def test_api_call_header(self):
        headers = {}
        twitch.api_call('botgotsthis', 'GET', '/kraken/', headers=headers)
        self.assertTrue(self.mock_clientid.called)
        self.assertTrue(self.mock_token.called)
        self.assertEqual(headers,
                         {'Accept': 'application/vnd.twitchtv.v3+json',
                          'Client-ID': '0123456789abcdef',
                          'Authorization': 'OAuth abcdef0123456789'})

    def test_chat_server(self):
        mock = MagicMock()
        self.mock_httpconnection.return_value.getresponse.return_value = mock
        mock.__enter__.return_value.read.return_value = chatServers
        self.assertEqual(twitch.chat_server('botgotsthis'), 'aws')

    def test_chat_server_except(self):
        mock = MagicMock()
        self.mock_httpconnection.return_value.getresponse.return_value = mock
        mock.__enter__.return_value.read.return_value = b''
        self.assertIsNone(twitch.chat_server('botgotsthis'))


class TestApiTwitch(unittest.TestCase):
    def setUp(self):
        self.mock_response = Mock(spec=HTTPResponse)
        patcher = patch('source.api.twitch.api_call')
        self.addCleanup(patcher.stop)
        self.mock_api_call = patcher.start()
        self.mock_api_call.return_value = [self.mock_response, b'']

    def test_server_time(self):
        timestamp = 'Sat, 1 Jan 2000 00:00:00 GMT'
        self.mock_response.status = 200
        self.mock_response.getheader.return_value = timestamp
        self.assertEqual(twitch.server_time(), datetime(2000, 1, 1))

    def test_server_time_except(self):
        self.mock_api_call.side_effect = HTTPException
        self.assertIsNone(twitch.server_time())

    def test_twitch_emotes(self):
        self.mock_response.status = 200
        self.mock_api_call.return_value[1] = twitchEmotes
        self.assertEqual(twitch.twitch_emotes(), ({25: 'Kappa'}, {25: 0}))

    def test_twitch_emotes_special(self):
        self.mock_response.status = 200
        self.mock_api_call.return_value[1] = twitchEmotesSpecial
        self.assertEqual(
            twitch.twitch_emotes()[0],
            {7: 'B)',
             5: ':z',
             1: ':)',
             2: ':(',
             12: ':P',
             13: ';P',
             9: '<3',
             11: ';)',
             14: 'R)',
             3: ':D',
             8: ':o',
             4: '>('})

    def test_twitch_emotes_except(self):
        self.mock_api_call.side_effect = ConnectionError
        self.assertIsNone(twitch.twitch_emotes())

    @patch.dict('bot.globals.globalSessionData')
    def test_is_valid_user(self):
        bot.globals.globalSessionData['validTwitchUser'] = defaultdict(
            lambda: (datetime.min, None))
        self.mock_response.code = 200
        self.assertIs(twitch.is_valid_user('botgotsthis'), True)

    @patch.dict('bot.globals.globalSessionData')
    def test_is_valid_user_except(self):
        bot.globals.globalSessionData['validTwitchUser'] = defaultdict(
            lambda: (datetime.min, None))
        self.mock_api_call.side_effect = ConnectionError
        self.assertIsNone(twitch.is_valid_user('botgotsthis'))

    def test_num_followers(self):
        self.mock_api_call.return_value[1] = numFollowers
        self.assertEqual(twitch.num_followers('botgotsthis'), 1)

    def test_num_followers_except(self):
        self.mock_api_call.side_effect = ConnectionError
        self.assertIsNone(twitch.num_followers('botgotsthis'))

    def test_update(self):
        self.assertIsNone(twitch.update('botgotsthis'))
        self.assertFalse(self.mock_api_call.called)

    def test_update_status(self):
        self.mock_response.status = 200
        self.assertIs(twitch.update('botgotsthis', status=''), True)
        self.mock_api_call.assert_called_once_with(
            'botgotsthis', 'PUT', StrContains(), headers=TypeMatch(dict),
            data={'channel[status]': ' '})

    def test_update_game(self):
        self.mock_response.status = 200
        self.assertIs(twitch.update('botgotsthis', game=''), True)
        self.mock_api_call.assert_called_once_with(
            'botgotsthis', 'PUT', StrContains(), headers=TypeMatch(dict),
            data={'channel[game]': ''})

    def test_update_except(self):
        self.mock_api_call.side_effect = HTTPException
        self.assertIsNone(twitch.update('botgotsthis', status='Kappa'))

    def test_active_streams(self):
        self.mock_response.status = 404
        self.assertIsNone(twitch.update('botgotsthis'))
        self.assertFalse(self.mock_api_call.called)

    @patch('source.api.twitch._handle_streams')
    def test_active_streams_one(self, mock_handle):
        self.mock_response.status = 200
        self.mock_api_call.return_value[1] = noStreams
        self.assertEqual(twitch.active_streams(['botgotsthis']), {})
        self.assertEqual(mock_handle.call_count, 1)

    @patch('source.api.twitch._handle_streams')
    def test_active_streams_too_many(self, mock_handle):
        self.mock_response.status = 200
        self.mock_api_call.side_effect = [
            [self.mock_response, multiStreams],
            [self.mock_response, noStreams]
        ]
        self.assertEqual(twitch.active_streams(['botgotsthis']), {})
        self.assertEqual(mock_handle.call_count, 2)

    def test_handle_streams(self):
        online = {}
        twitch._handle_streams(json.loads(streams), online)
        self.assertEqual(online,
                         {'botgotsthis': twitch.TwitchStatus(
                             datetime(2000, 1, 1), None, None)})

    def test_active_streams_404(self):
        self.mock_response.status = 404
        self.assertIsNone(twitch.channel_properties('botgotsthis'))

    def test_active_streams_exception(self):
        self.mock_api_call.side_effect = HTTPException
        self.assertIsNone(twitch.channel_properties('botgotsthis'))

    def test_active_streams_something(self):
        self.mock_response.status = 200
        self.mock_api_call.return_value[1] = channelProperties
        self.assertEqual(twitch.channel_properties('botgotsthis'),
                         twitch.TwitchStatus(None, None, None))
