import asyncio
import bot  # noqa: F401
import json

import aiohttp
import asynctest

from datetime import datetime
from http.client import HTTPException, HTTPResponse
from source.api import twitch
from tests.unittest.mock_class import StrContains, TypeMatch
from asynctest.mock import MagicMock, Mock, patch

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
}'''  # noqa: E501

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
}'''  # noqa: E501

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
}'''  # noqa: E501

streams = '''[
    {
        "_id": 1,
        "game": null,
        "community_id":"",
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
]'''  # noqa: E501

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
}'''  # noqa: E501


twitchIdReponse = b'''\
{"_total":1,"users":[{"display_name":"BotGotsThis","_id":"1","name":"botgotsthis","type":"user","bio":null,"created_at":"2000-01-01T00:00:00.000000Z","updated_at":"2000-01-01T00:00:00.000000Z","logo":null}]}'''  # noqa: E501


speedrunCommunityResponse = r'''{"_id":"6e940c4a-c42f-47d2-af83-0a2c7e47c421","owner_id":"23406143","name":"Speedrunning","summary":"Welcome to the Speedrunning Community, we like to play games fast! Connect with fellow speedrun enthusiasts by watching and/or streaming speedruns here!","description":"Welcome to the Speedrunning Community, we like to play games fast! Speedrunners are an extremely diverse and welcoming group that enjoys games of all genres, consoles, and eras! Speedrunners enjoy collaborating to optimize games by finding time saving tricks and glitches, to drive speedrun times as low as possible. Whether you are going for a world record or just trying to learn or improve at a game you will find yourself at home here. Speedrunners often organize online and live speedrunning events that benefit charities or are just for fun. If you enjoy friendly competition you can find it in the form of races and tournaments that are typically open to join. \n\n**Resources:**\n[Speed Runs Live](http://www.speedrunslive.com) race games here.\n[speedrun.com](http://www.speedrun.com)  leaderboards and more.\n[SpeedGaming](http://speedgaming.org) hosts tournaments and events.\n[GamesDoneQuick](http://www.gamesdonequick.com) live marathons for charity.\n[TASVideos.org](http://tasvideos.org)  tool-assisted speedruns, and more.","description_html":"Welcome to the Speedrunning Community, we like to play games fast! Speedrunners are an extremely diverse and welcoming group that enjoys games of all genres, consoles, and eras! Speedrunners enjoy collaborating to optimize games by finding time saving tricks and glitches, to drive speedrun times as low as possible. Whether you are going for a world record or just trying to learn or improve at a game you will find yourself at home here. Speedrunners often organize online and live speedrunning events that benefit charities or are just for fun. If you enjoy friendly competition you can find it in the form of races and tournaments that are typically open to join.\u003cbr\u003e\u003cbr\u003e\u003cstrong\u003eResources:\u003c/strong\u003e\u003cbr\u003e\n\u003ca href=\"http://www.speedrunslive.com\" rel=\"nofollow noreferrer noopener\" target=\"_blank\"\u003eSpeed Runs Live\u003c/a\u003e race games here.\u003cbr\u003e\n\u003ca href=\"http://www.speedrun.com\" rel=\"nofollow noreferrer noopener\" target=\"_blank\"\u003espeedrun.com\u003c/a\u003e  leaderboards and more.\u003cbr\u003e\n\u003ca href=\"http://speedgaming.org\" rel=\"nofollow noreferrer noopener\" target=\"_blank\"\u003eSpeedGaming\u003c/a\u003e hosts tournaments and events.\u003cbr\u003e\n\u003ca href=\"http://www.gamesdonequick.com\" rel=\"nofollow noreferrer noopener\" target=\"_blank\"\u003eGamesDoneQuick\u003c/a\u003e live marathons for charity.\u003cbr\u003e\n\u003ca href=\"http://tasvideos.org\" rel=\"nofollow noreferrer noopener\" target=\"_blank\"\u003eTASVideos.org\u003c/a\u003e  tool-assisted speedruns, and more.\u003cbr\u003e","rules":"Broadcast speedrunning content, where “speedrunning” is defined as completing a video game, or predetermined goal/set of goals within a video game as fast as possible.\n\n- Racing and racing formats including bingo, randomizer, and blind are allowed\n- Individual Level (IL) formats are allowed\n- Learning, routing, and practicing speedruns is allowed.\n- Tool Assisted Speedrunning (TAS) is allowed\n- Non-speedrunning content is not allowed.\n\nHave questions about the rules? Contact moderators listed below:\n\n360chrism\nAuthorblues\nFeasel\nMrcab55\nRomscout\nSinister1 (leader)\nSpikevegeta\nThadarkman78","rules_html":"Broadcast speedrunning content, where “speedrunning” is defined as completing a video game, or predetermined goal/set of goals within a video game as fast as possible.\u003cbr\u003e\u003cbr\u003e\n\u003cul\u003e\n\u003cli\u003eRacing and racing formats including bingo, randomizer, and blind are allowed\u003cbr\u003e\u003c/li\u003e\n\u003cli\u003eIndividual Level (IL) formats are allowed\u003cbr\u003e\u003c/li\u003e\n\u003cli\u003eLearning, routing, and practicing speedruns is allowed.\u003cbr\u003e\u003c/li\u003e\n\u003cli\u003eTool Assisted Speedrunning (TAS) is allowed\u003cbr\u003e\u003c/li\u003e\n\u003cli\u003eNon-speedrunning content is not allowed.\u003cbr\u003e\n\u003cbr\u003e\u003c/li\u003e\n\u003c/ul\u003e\nHave questions about the rules? Contact moderators listed below:\u003cbr\u003e\u003cbr\u003e360chrism\u003cbr\u003e\nAuthorblues\u003cbr\u003e\nFeasel\u003cbr\u003e\nMrcab55\u003cbr\u003e\nRomscout\u003cbr\u003e\nSinister1 (leader)\u003cbr\u003e\nSpikevegeta\u003cbr\u003e\nThadarkman78\u003cbr\u003e","language":"EN","avatar_image_url":"https://static-cdn.jtvnw.net/twitch-community-images-production/6e940c4a-c42f-47d2-af83-0a2c7e47c421/43b0ac6d-ee00-4292-b6e8-cfab0f81e53f.png","cover_image_url":""}'''.encode()  # noqa: E501


class TestApiTwitchApiHeaders(asynctest.TestCase):
    def setUp(self):
        patcher = patch('bot.config')
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.twitchClientId = '0123456789abcdef'

        patcher = patch('source.api.oauth.token')
        self.addCleanup(patcher.stop)
        self.mock_token = patcher.start()
        self.mock_token.return_value = 'abcdef0123456789'

    async def test_get_headers(self):
        headers = await twitch.get_headers({}, 'botgotsthis')
        self.mock_token.assert_called_once_with('botgotsthis')
        self.assertEqual(headers,
                         {'Accept': 'application/vnd.twitchtv.v5+json',
                          'Client-ID': '0123456789abcdef',
                          'Authorization': 'OAuth abcdef0123456789'})

    async def test_get_headers_no_channel(self):
        headers = await twitch.get_headers({}, None)
        self.assertFalse(self.mock_token.called)
        self.assertEqual(headers,
                         {'Accept': 'application/vnd.twitchtv.v5+json',
                          'Client-ID': '0123456789abcdef'})


class TestApiTwitchApiCalls(asynctest.TestCase):
    def setUp(self):
        patcher = patch('source.api.twitch.get_headers')
        self.addCleanup(patcher.stop)
        self.mock_headers = patcher.start()
        self.mock_headers.return_value = {}

        self.mock_session = MagicMock(spec=aiohttp.ClientSession)
        self.mock_session.__aenter__.return_value = self.mock_session
        self.mock_session.__aexit__.return_value = False

        patcher = patch('aiohttp.ClientSession')
        self.addCleanup(patcher.stop)
        self.mock_clientsession = patcher.start()
        self.mock_clientsession.return_value = self.mock_session

        self.mock_response = MagicMock(spec=aiohttp.ClientResponse)
        self.mock_response.__aenter__.return_value = self.mock_response
        self.mock_response.__aexit__.return_value = False
        self.mock_response.status = 200
        self.mock_response.json.return_value = {}

    async def test_get_call(self):
        self.mock_session.get.return_value = self.mock_response
        self.assertEqual(await twitch.get_call('botgotsthis', '/kraken/'),
                         (self.mock_response, {}))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.get.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_get_call_channel_none(self):
        self.mock_session.get.return_value = self.mock_response
        self.assertEqual(await twitch.get_call(None, '/kraken/'),
                         (self.mock_response, {}))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.get.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, None)

    async def test_get_call_header(self):
        headers = {'Kappa': 'megotsthis'}
        self.mock_session.get.return_value = self.mock_response
        self.assertEqual(
            await twitch.get_call('botgotsthis', '/kraken/', headers=headers),
            (self.mock_response, {}))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.get.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({'Kappa': 'megotsthis'},
                                                  'botgotsthis')

    async def test_get_call_204(self):
        self.mock_session.get.return_value = self.mock_response
        self.mock_response.json.side_effect = ValueError
        self.mock_response.status = 204
        self.assertEqual(
            await twitch.get_call('botgotsthis', '/kraken/'),
            (self.mock_response, None))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.get.called)
        self.assertFalse(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_get_call_except(self):
        self.mock_session.get.return_value = self.mock_response
        excp = aiohttp.ClientResponseError(None, None)
        self.mock_response.json.side_effect = excp
        self.assertEqual(
            await twitch.get_call('botgotsthis', '/kraken/'),
            (self.mock_response, None))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.get.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_post_call(self):
        self.mock_session.post.return_value = self.mock_response
        self.assertEqual(await twitch.post_call('botgotsthis', '/kraken/'),
                         (self.mock_response, {}))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.post.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_post_call_channel_none(self):
        self.mock_session.post.return_value = self.mock_response
        await twitch.post_call(None, '/kraken/')
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.post.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, None)

    async def test_post_call_header(self):
        self.mock_session.post.return_value = self.mock_response
        headers = {'Kappa': 'megotsthis'}
        await twitch.post_call('botgotsthis', '/kraken/', data=headers)
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.post.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_post_call_data(self):
        self.mock_session.post.return_value = self.mock_response
        data = {'bot': 'BotGotsThis'}
        await twitch.post_call('botgotsthis', '/kraken/', data=data)
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.post.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_post_call_204(self):
        self.mock_session.post.return_value = self.mock_response
        self.mock_response.json.side_effect = ValueError
        self.mock_response.status = 204
        self.assertEqual(
            await twitch.post_call('botgotsthis', '/kraken/'),
            (self.mock_response, None))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.post.called)
        self.assertFalse(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_post_call_except(self):
        self.mock_session.post.return_value = self.mock_response
        excp = aiohttp.ClientResponseError(None, None)
        self.mock_response.json.side_effect = excp
        self.assertEqual(
            await twitch.post_call('botgotsthis', '/kraken/'),
            (self.mock_response, None))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.post.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_put_call(self):
        self.mock_session.put.return_value = self.mock_response
        self.assertEqual(await twitch.put_call('botgotsthis', '/kraken/'),
                         (self.mock_response, {}))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.put.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_put_call_channel_none(self):
        self.mock_session.put.return_value = self.mock_response
        await twitch.put_call(None, '/kraken/')
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.put.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, None)

    async def test_put_call_header(self):
        self.mock_session.put.return_value = self.mock_response
        headers = {'Kappa': 'megotsthis'}
        await twitch.put_call('botgotsthis', '/kraken/', data=headers)
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.put.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_put_call_data(self):
        self.mock_session.put.return_value = self.mock_response
        data = {'bot': 'BotGotsThis'}
        await twitch.put_call('botgotsthis', '/kraken/', data=data)
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.put.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_put_call_204(self):
        self.mock_session.put.return_value = self.mock_response
        self.mock_response.json.side_effect = ValueError
        self.mock_response.status = 204
        self.assertEqual(
            await twitch.put_call('botgotsthis', '/kraken/'),
            (self.mock_response, None))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.put.called)
        self.assertFalse(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_put_call_except(self):
        self.mock_session.put.return_value = self.mock_response
        excp = aiohttp.ClientResponseError(None, None)
        self.mock_response.json.side_effect = excp
        self.assertEqual(
            await twitch.put_call('botgotsthis', '/kraken/'),
            (self.mock_response, None))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.put.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_delete_call(self):
        self.mock_session.delete.return_value = self.mock_response
        self.assertEqual(await twitch.delete_call('botgotsthis', '/kraken/'),
                         (self.mock_response, {}))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.delete.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_delete_call_channel_none(self):
        self.mock_session.delete.return_value = self.mock_response
        await twitch.delete_call(None, '/kraken/')
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.delete.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, None)

    async def test_delete_call_header(self):
        self.mock_session.delete.return_value = self.mock_response
        headers = {'Kappa': 'megotsthis'}
        await twitch.delete_call('botgotsthis', '/kraken/', data=headers)
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.delete.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_delete_call_data(self):
        self.mock_session.delete.return_value = self.mock_response
        data = {'bot': 'BotGotsThis'}
        await twitch.delete_call('botgotsthis', '/kraken/', data=data)
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.delete.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_delete_call_204(self):
        self.mock_session.delete.return_value = self.mock_response
        self.mock_response.json.side_effect = ValueError
        self.mock_response.status = 204
        self.assertEqual(
            await twitch.delete_call('botgotsthis', '/kraken/'),
            (self.mock_response, None))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.delete.called)
        self.assertFalse(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_delete_call_except(self):
        self.mock_session.delete.return_value = self.mock_response
        excp = aiohttp.ClientResponseError(None, None)
        self.mock_response.json.side_effect = excp
        self.assertEqual(
            await twitch.delete_call('botgotsthis', '/kraken/'),
            (self.mock_response, None))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.delete.called)
        self.assertTrue(self.mock_response.json.called)
        self.mock_headers.assert_called_once_with({}, 'botgotsthis')

    async def test_chat_server(self):
        self.mock_session.get.return_value = self.mock_response
        self.mock_response.json.return_value = json.loads(chatServers.decode())
        self.assertEqual(await twitch.chat_server('botgotsthis'), 'aws')
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.get.called)
        self.assertTrue(self.mock_response.json.called)

    async def test_chat_server_except(self):
        self.mock_session.get.return_value = self.mock_response
        self.mock_response.json.side_effect = ValueError
        self.assertIsNone(await twitch.chat_server('botgotsthis'))
        self.assertTrue(self.mock_clientsession.called)
        self.assertTrue(self.mock_session.get.called)
        self.assertTrue(self.mock_response.json.called)


class TestApiTwitch(asynctest.TestCase):
    def setUp(self):
        self.mock_async_response = Mock(spec=aiohttp.ClientResponse)
        self.mock_response = Mock(spec=HTTPResponse)

        patcher = patch('source.api.twitch.get_call')
        self.addCleanup(patcher.stop)
        self.mock_get_call = patcher.start()
        self.mock_get_call.return_value = [self.mock_async_response, None]

        patcher = patch('source.api.twitch.post_call')
        self.addCleanup(patcher.stop)
        self.mock_post_call = patcher.start()
        self.mock_post_call.return_value = [self.mock_async_response, None]

        patcher = patch('source.api.twitch.put_call')
        self.addCleanup(patcher.stop)
        self.mock_put_call = patcher.start()
        self.mock_put_call.return_value = [self.mock_async_response, None]

        patcher = patch('source.api.twitch.delete_call')
        self.addCleanup(patcher.stop)
        self.mock_delete_call = patcher.start()
        self.mock_delete_call.return_value = [self.mock_async_response, None]

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.twitchId = {
            'botgotsthis': '0',
            'megotsthis': None,
            }
        self.mock_globals.twitchCommunity = {
            'speedrunning': '6e940c4a-c42f-47d2-af83-0a2c7e47c421',
            'abc': None,
            }

        patcher = patch('bot.utils.loadTwitchId')
        self.addCleanup(patcher.stop)
        self.mock_load = patcher.start()
        self.mock_load.return_value = True

    async def test_server_time(self):
        timestamp = 'Sat, 1 Jan 2000 00:00:00 GMT'
        self.mock_async_response.status = 200
        self.mock_async_response.headers = {}
        self.mock_async_response.headers['Date'] = timestamp
        self.mock_get_call.return_value[1] = {}
        self.assertEqual(await twitch.server_time(), datetime(2000, 1, 1))

    async def test_server_time_except(self):
        exception = aiohttp.ClientResponseError(None, None)
        self.mock_get_call.side_effect = exception
        self.assertIsNone(await twitch.server_time())

    async def test_twitch_emotes(self):
        self.mock_async_response.status = 200
        self.mock_get_call.return_value[1] = json.loads(twitchEmotes)
        self.assertEqual(await twitch.twitch_emotes(),
                         ({25: 'Kappa'}, {25: 0}))
        self.mock_get_call.assert_called_once_with(
            None, StrContains('/kraken/chat/emoticon_images?emotesets='))

    async def test_twitch_emotes_special(self):
        self.mock_async_response.status = 200
        self.mock_get_call.return_value[1] = json.loads(twitchEmotesSpecial)
        self.assertEqual(
            (await twitch.twitch_emotes())[0],
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
        self.mock_get_call.assert_called_once_with(
            None, StrContains('/kraken/chat/emoticon_images?emotesets='))

    async def test_twitch_emotes_except(self):
        self.mock_get_call.side_effect = asyncio.TimeoutError
        self.assertIsNone(await twitch.twitch_emotes())
        self.mock_get_call.assert_called_once_with(
            None, StrContains('/kraken/chat/emoticon_images?emotesets='))

    async def test_is_valid_user(self):
        self.assertIs(await twitch.is_valid_user('botgotsthis'), True)
        self.mock_load.assert_called_once_with('botgotsthis')

    async def test_is_valid_user_false(self):
        self.assertIs(await twitch.is_valid_user('megotsthis'), False)
        self.mock_load.assert_called_once_with('megotsthis')

    async def test_is_valid_user_no_load(self):
        self.mock_load.return_value = False
        self.assertIsNone(await twitch.is_valid_user('botgotsthis'))
        self.mock_load.assert_called_once_with('botgotsthis')

    async def test_num_followers(self):
        data = json.loads(numFollowers.decode())
        self.mock_get_call.return_value[1] = data
        self.assertEqual(await twitch.num_followers('botgotsthis'), 1)
        self.mock_load.assert_called_once_with('botgotsthis')

    async def test_num_followers_no_load(self):
        self.mock_load.return_value = False
        self.assertIsNone(await twitch.num_followers('botgotsthis'))
        self.mock_load.assert_called_once_with('botgotsthis')

    async def test_num_followers_no_user(self):
        self.assertEqual(await twitch.num_followers('megotsthis'), 0)
        self.mock_load.assert_called_once_with('megotsthis')

    async def test_num_followers_except(self):
        self.mock_load.return_value = False
        self.assertIsNone(await twitch.num_followers('botgotsthis'))

    async def test_update(self):
        self.assertIsNone(await twitch.update('botgotsthis'))
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertFalse(self.mock_put_call.called)

    async def test_update_no_load(self):
        self.mock_load.return_value = False
        self.assertIsNone(await twitch.update('botgotsthis'))
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertFalse(self.mock_put_call.called)

    async def test_update_no_user(self):
        self.assertIsNone(await twitch.update('megotsthis'))
        self.mock_load.assert_called_once_with('megotsthis')
        self.assertFalse(self.mock_put_call.called)

    async def test_update_status(self):
        self.mock_async_response.status = 200
        self.assertIs(await twitch.update('botgotsthis', status=''), True)
        self.mock_load.assert_called_once_with('botgotsthis')
        self.mock_put_call.assert_called_once_with(
            'botgotsthis', StrContains(), headers=TypeMatch(dict),
            data={'channel[status]': ' '})

    async def test_update_game(self):
        self.mock_async_response.status = 200
        self.assertIs(await twitch.update('botgotsthis', game=''), True)
        self.mock_load.assert_called_once_with('botgotsthis')
        self.mock_put_call.assert_called_once_with(
            'botgotsthis', StrContains(), headers=TypeMatch(dict),
            data={'channel[game]': ''})

    async def test_update_except(self):
        exception = aiohttp.ClientResponseError(None, None)
        self.mock_put_call.side_effect = exception
        self.assertIsNone(await twitch.update('botgotsthis'))
        self.assertFalse(self.mock_put_call.called)
        self.mock_load.assert_called_once_with('botgotsthis')

    @patch('source.api.twitch._handle_streams')
    async def test_active_streams_no_load(self, mock_handle):
        self.mock_load.return_value = False
        self.assertEqual(await twitch.active_streams(['botgotsthis']), {})
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertFalse(self.mock_get_call.called)
        self.assertEqual(mock_handle.call_count, 0)

    @patch('source.api.twitch._handle_streams')
    async def test_active_streams_no_user(self, mock_handle):
        self.assertEqual(await twitch.active_streams(['megotsthis']), {})
        self.mock_load.assert_called_once_with('megotsthis')
        self.assertFalse(self.mock_get_call.called)
        self.assertEqual(mock_handle.call_count, 0)

    @patch('source.api.twitch._handle_streams')
    async def test_active_streams_404(self, mock_handle):
        self.mock_async_response.status = 404
        self.assertIsNone(await twitch.active_streams(['botgotsthis']))
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertEqual(mock_handle.call_count, 0)

    @patch('source.api.twitch._handle_streams')
    async def test_active_streams_one(self, mock_handle):
        self.mock_async_response.status = 200
        self.mock_get_call.return_value[1] = json.loads(noStreams.decode())
        self.assertEqual(await twitch.active_streams(['botgotsthis']), {})
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertEqual(mock_handle.call_count, 1)

    @patch('source.api.twitch._handle_streams')
    async def test_active_streams_too_many(self, mock_handle):
        self.mock_async_response.status = 200
        self.mock_get_call.side_effect = [
            [self.mock_async_response, json.loads(multiStreams.decode())],
            [self.mock_async_response, json.loads(noStreams.decode())]
        ]
        self.assertEqual(await twitch.active_streams(['botgotsthis']), {})
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertEqual(mock_handle.call_count, 2)

    @asynctest.fail_on(unused_loop=False)
    def test_handle_streams(self):
        online = {}
        twitch._handle_streams(json.loads(streams), online)
        self.assertEqual(online,
                         {'botgotsthis': twitch.TwitchStatus(
                             datetime(2000, 1, 1), None, None, None)})

    @asynctest.fail_on(unused_loop=False)
    def test_handle_streams_community(self):
        online = {}
        data = json.loads(streams)
        data[0]['community_id'] = '1'
        twitch._handle_streams(data, online)
        self.assertEqual(online,
                         {'botgotsthis': twitch.TwitchStatus(
                             datetime(2000, 1, 1), None, None, '1')})

    async def test_properties_no_load(self):
        self.mock_load.return_value = False
        self.assertIsNone(await twitch.channel_properties('botgotsthis'))
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertFalse(self.mock_get_call.called)

    async def test_properties_404(self):
        self.mock_async_response.status = 404
        self.assertIsNone(await twitch.channel_properties('botgotsthis'))
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertTrue(self.mock_get_call.called)

    async def test_properties_exception(self):
        self.mock_get_call.side_effect = asyncio.TimeoutError
        self.assertIsNone(await twitch.channel_properties('botgotsthis'))
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertTrue(self.mock_get_call.called)

    async def test_properties_something(self):
        self.mock_async_response.status = 200
        data = json.loads(channelProperties.decode())
        self.mock_get_call.return_value[1] = data
        self.assertEqual(await twitch.channel_properties('botgotsthis'),
                         twitch.TwitchStatus(None, None, None, None))
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertTrue(self.mock_get_call.called)

    async def test_twitch_ids(self):
        self.mock_async_response.status = 200
        data = twitchIdReponse.decode()
        self.mock_get_call.return_value[1] = json.loads(data)
        self.assertEqual(
            await twitch.getTwitchIds(['botgotsthis', 'megotsthis']),
            {'botgotsthis': '1'})

    async def test_twitch_ids_404(self):
        self.mock_async_response.status = 404
        self.assertIsNone(
            await twitch.getTwitchIds(['botgotsthis', 'megotsthis']))

    async def test_twitch_ids_exception(self):
        self.mock_get_call.side_effect = asyncio.TimeoutError
        self.assertIsNone(
            await twitch.getTwitchIds(['botgotsthis', 'megotsthis']))

    async def test_channel_community_no_load(self):
        self.mock_load.return_value = False
        self.assertIsNone(await twitch.channel_community('botgotsthis'))
        self.mock_load.assert_called_once_with('botgotsthis')

    async def test_channel_community_no_user(self):
        self.assertIsNone(await twitch.channel_community('megotsthis'))
        self.mock_load.assert_called_once_with('megotsthis')

    async def test_channel_community_404(self):
        self.mock_async_response.status = 404
        self.assertIsNone(await twitch.channel_community('botgotsthis'))
        self.mock_load.assert_called_once_with('botgotsthis')

    async def test_channel_community_exception(self):
        self.mock_get_call.side_effect = HTTPException
        self.assertIsNone(await twitch.channel_community('botgotsthis'))
        self.mock_load.assert_called_once_with('botgotsthis')

    async def test_channel_community(self):
        self.mock_async_response.status = 200
        data = json.loads(speedrunCommunityResponse.decode())
        self.mock_get_call.return_value[1] = data
        self.assertEqual(await twitch.channel_community('botgotsthis'),
                         twitch.TwitchCommunity('6e940c4a-c42f-47d2-'
                                                'af83-0a2c7e47c421',
                                                'Speedrunning'))
        self.mock_load.assert_called_once_with('botgotsthis')

    async def test_channel_community_None(self):
        self.mock_async_response.status = 204
        self.assertEqual(await twitch.channel_community('botgotsthis'),
                         twitch.TwitchCommunity(None, None))
        self.mock_load.assert_called_once_with('botgotsthis')

    async def test_get_community_404(self):
        self.mock_async_response.status = 404
        self.assertEqual(await twitch.get_community('speedrunning'),
                         twitch.TwitchCommunity(None, None))

    async def test_get_community_exception(self):
        exception = aiohttp.ClientResponseError(None, None)
        self.mock_get_call.side_effect = exception
        self.assertIsNone(await twitch.get_community('speedrunning'))

    async def test_get_community(self):
        self.mock_async_response.status = 200
        data = json.loads(speedrunCommunityResponse.decode())
        self.mock_get_call.return_value[1] = data
        id = '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
        self.assertEqual(await twitch.get_community('speedrunning'),
                         twitch.TwitchCommunity(id, 'Speedrunning'))

    async def test_get_community_urlencode(self):
        self.mock_async_response.status = 404
        self.assertEqual(await twitch.get_community('???'),
                         twitch.TwitchCommunity(None, None))
        self.mock_get_call.assert_called_once_with(
            None, '/kraken/communities?name=%3F%3F%3F')

    async def test_get_community_id_404(self):
        self.mock_async_response.status = 404
        id = '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
        self.assertEqual(await twitch.get_community_by_id(id),
                         twitch.TwitchCommunity(None, None))

    async def test_get_community_id_exception(self):
        exception = aiohttp.ClientResponseError(None, None)
        self.mock_get_call.side_effect = exception
        id = '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
        self.assertIsNone(await twitch.get_community_by_id(id))

    async def test_get_community_id(self):
        self.mock_async_response.status = 200
        data = json.loads(speedrunCommunityResponse.decode())
        self.mock_get_call.return_value[1] = data
        id = '6e940c4a-c42f-47d2-af83-0a2c7e47c421'
        self.assertEqual(await twitch.get_community_by_id(id),
                         twitch.TwitchCommunity(id, 'Speedrunning'))

    @patch('bot.utils.loadTwitchCommunity')
    async def test_set_channel_community_no_load(self, mock_community):
        self.mock_load.return_value = False
        mock_community.return_value = True
        self.assertIsNone(
            await twitch.set_channel_community('botgotsthis', 'Speedrunning'))
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertFalse(mock_community.called)

    @patch('bot.utils.loadTwitchCommunity')
    async def test_set_channel_community_no_user(self, mock_community):
        mock_community.return_value = True
        self.assertIsNone(
            await twitch.set_channel_community('megotsthis', 'Speedrunning'))
        self.mock_load.assert_called_once_with('megotsthis')
        self.assertFalse(mock_community.called)

    @patch('bot.utils.loadTwitchCommunity')
    async def test_set_channel_community_no_load_community(
            self, mock_community):
        mock_community.return_value = False
        self.assertIsNone(
            await twitch.set_channel_community('botgotsthis', 'Speedrunning'))
        self.mock_load.assert_called_once_with('botgotsthis')
        mock_community.assert_called_once_with('Speedrunning')

    @patch('bot.utils.loadTwitchCommunity')
    async def test_set_channel_community_no_community(self, mock_community):
        mock_community.return_value = True
        self.assertIs(
            await twitch.set_channel_community('botgotsthis', 'ABC'),
            False)
        self.mock_load.assert_called_once_with('botgotsthis')
        mock_community.assert_called_once_with('ABC')

    @patch('bot.utils.loadTwitchCommunity')
    async def test_set_channel_community_404(self, mock_community):
        mock_community.return_value = True
        self.mock_async_response.status = 404
        self.assertIsNone(
            await twitch.set_channel_community('botgotsthis', 'Speedrunning'))
        self.mock_load.assert_called_once_with('botgotsthis')
        mock_community.assert_called_once_with('Speedrunning')

    @patch('bot.utils.loadTwitchCommunity')
    async def test_set_channel_community_none_404(self, mock_community):
        mock_community.return_value = True
        self.mock_async_response.status = 404
        self.assertIsNone(
            await twitch.set_channel_community('botgotsthis', None))
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertFalse(mock_community.called)

    @patch('bot.utils.loadTwitchCommunity')
    async def test_set_channel_community_exception(self, mock_community):
        mock_community.return_value = True
        exception = aiohttp.ClientResponseError(None, None)
        self.mock_put_call.side_effect = exception
        self.assertIsNone(
            await twitch.set_channel_community('botgotsthis', 'Speedrunning'))
        self.mock_load.assert_called_once_with('botgotsthis')
        mock_community.assert_called_once_with('Speedrunning')

    @patch('bot.utils.loadTwitchCommunity')
    async def test_set_channel_community_exception_2(self, mock_community):
        mock_community.return_value = True
        exception = aiohttp.ClientResponseError(None, None)
        self.mock_delete_call.side_effect = exception
        self.assertIsNone(
            await twitch.set_channel_community('botgotsthis', None))
        self.mock_load.assert_called_once_with('botgotsthis')

    @patch('bot.utils.loadTwitchCommunity')
    async def test_set_channel_community(self, mock_community):
        mock_community.return_value = True
        self.mock_async_response.status = 204
        self.assertIs(
            await twitch.set_channel_community('botgotsthis', 'Speedrunning'),
            True)
        self.mock_load.assert_called_once_with('botgotsthis')
        mock_community.assert_called_once_with('Speedrunning')
        self.mock_put_call.assert_called_once_with(
            'botgotsthis', StrContains())

    @patch('bot.utils.loadTwitchCommunity')
    async def test_set_channel_community_none(self, mock_community):
        mock_community.return_value = True
        self.mock_async_response.status = 204
        self.assertIs(
            await twitch.set_channel_community('botgotsthis', None),
            True)
        self.mock_load.assert_called_once_with('botgotsthis')
        self.assertFalse(mock_community.called)
        self.mock_delete_call.assert_called_once_with(
            'botgotsthis', StrContains())
