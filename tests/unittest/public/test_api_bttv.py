import asynctest
import json

import aiohttp

from source.api import bttv
from asynctest.mock import MagicMock, patch

globalEmotes = b'''{
    "status": 200,
    "urlTemplate": "//cdn.betterttv.net/emote/{{id}}/{{image}}",
    "emotes": [
        {
            "id": "54fa925e01e468494b85b54d",
            "code": "OhMyGoodness",
            "channel": null,
            "restrictions": {
                "channels": [],
                "games": []
            },
            "imageType": "png"
        }
    ]
}'''

broadcasterEmotes = b'''{
    "status": 200,
    "urlTemplate": "//cdn.betterttv.net/emote/{{id}}/{{image}}",
    "bots": [],
    "emotes": [
        {
            "id": "554da1a289d53f2d12781907",
            "channel": "NightDev",
            "code": "(ditto)",
            "imageType": "gif"
        }
    ]
}'''


class TestApiBttv(asynctest.TestCase):
    def setUp(self):
        self.mock_response = MagicMock(spec=aiohttp.ClientResponse)
        self.mock_response.__aenter__.return_value = self.mock_response
        self.mock_response.__aexit__.return_value = False
        self.mock_response.status = 200
        self.mock_response.json.return_value = {}

        self.mock_session = MagicMock(spec=aiohttp.ClientSession)
        self.mock_session.__aenter__.return_value = self.mock_session
        self.mock_session.__aexit__.return_value = False
        self.mock_session.get.return_value = self.mock_response

        patcher = patch('aiohttp.ClientSession')
        self.addCleanup(patcher.stop)
        self.mock_clientsession = patcher.start()
        self.mock_clientsession.return_value = self.mock_session

    async def fail_test_globalEmotes(self):
        data = json.loads(globalEmotes.decode())
        self.mock_response.json.return_value = data
        self.assertEqual(await bttv.getGlobalEmotes(),
                         {'54fa925e01e468494b85b54d': 'OhMyGoodness'})

    async def fail_test_globalEmotes_404(self):
        exception = aiohttp.ClientResponseError(None, None, code=404)
        self.mock_session.get.side_effect = exception
        self.assertEqual(await bttv.getGlobalEmotes(), {})

    async def fail_test_globalEmotes_error(self):
        exception = aiohttp.ClientResponseError(None, None)
        self.mock_session.get.side_effect = exception
        self.assertIsNone(await bttv.getGlobalEmotes())

    async def fail_test_broadcasterEmotes(self):
        data = json.loads(broadcasterEmotes.decode())
        self.mock_response.json.return_value = data
        self.assertEqual(await bttv.getBroadcasterEmotes('pokemonspeedrunstv'),
                         {'554da1a289d53f2d12781907': '(ditto)'})

    async def fail_test_broadcasterEmotes_404(self):
        exception = aiohttp.ClientResponseError(None, None, code=404)
        self.mock_session.get.side_effect = exception
        self.assertEqual(await bttv.getBroadcasterEmotes('pokemonspeedrunstv'),
                         {})

    async def fail_test_broadcasterEmotes_error(self):
        exception = aiohttp.ClientResponseError(None, None)
        self.mock_session.get.side_effect = exception
        self.assertIsNone(
            await bttv.getBroadcasterEmotes('pokemonspeedrunstv'))
