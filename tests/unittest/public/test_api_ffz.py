import asynctest
import json

import aiohttp

from source.api import ffz
from asynctest.mock import MagicMock, Mock, patch

globalEmotes = b'''{
    "default_sets": [
        3
    ],
    "sets": {
        "3": {
            "_type": 0,
            "css": null,
            "description": null,
            "emoticons": [
                {
                    "css": null,
                    "height": 33,
                    "hidden": false,
                    "id": 3,
                    "margins": null,
                    "name": "BeanieHipster",
                    "owner": {
                        "display_name": "dansalvato",
                        "id": 2,
                        "name": "dansalvato"
                    },
                    "public": false,
                    "urls": {
                        "1": "//cdn.frankerfacez.com/emoticon/3/1"
                    },
                    "width": 28
                }
            ],
            "icon": null,
            "id": 3,
            "title": "Global Emoticons"
        },
        "4330": {
            "_type": 0,
            "css": null,
            "description": null,
            "emoticons": [
                {
                    "css": null,
                    "height": 20,
                    "hidden": false,
                    "id": 29868,
                    "margins": null,
                    "name": "ChatPyramid",
                    "owner": {
                        "display_name": "SirStendec",
                        "id": 1,
                        "name": "sirstendec"
                    },
                    "public": true,
                    "urls": {
                        "1": "//cdn.frankerfacez.com/emoticon/29868/1",
                        "2": "//cdn.frankerfacez.com/emoticon/29868/2",
                        "4": "//cdn.frankerfacez.com/emoticon/29868/4"
                    },
                    "width": 62
                }
            ],
            "icon": null,
            "id": 4330,
            "title": ": Sten's Cheaty Emotes"
        }
    }
}'''

broadcasterEmotes = b'''{
    "room": {
        "_id": 14901,
        "_tid": 62323782,
        "css": null,
        "display_name": "PokemonSpeedrunsTV",
        "id": "pokemonspeedrunstv",
        "is_group": false,
        "moderator_badge": null,
        "set": 14901
    },
    "sets": {
        "14901": {
            "_type": 1,
            "css": null,
            "description": null,
            "emoticons": [
                {
                    "css": null,
                    "height": 26,
                    "hidden": false,
                    "id": 18146,
                    "margins": null,
                    "name": "KevinSquirtle",
                    "owner": {
                        "display_name": "Werster",
                        "id": 2656,
                        "name": "werster"
                    },
                    "public": true,
                    "urls": {
                        "1": "//cdn.frankerfacez.com/emoticon/18146/1"
                    },
                    "width": 30
                }
            ],
            "icon": null,
            "id": 14901,
            "title": "Channel: PokemonSpeedrunsTV"
        }
    }
}'''


class TestApiFfz(asynctest.TestCase):
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

    async def test_globalEmotes(self):
        data = json.loads(globalEmotes.decode())
        self.mock_response.json.return_value = data
        self.assertEqual(await ffz.getGlobalEmotes(), {3: 'BeanieHipster'})

    async def test_globalEmotes_404(self):
        exception = aiohttp.ClientResponseError(None, None, code=404)
        self.mock_session.get.side_effect = exception
        self.assertEqual(await ffz.getGlobalEmotes(), {})

    async def fail_test_globalEmotes_error(self):
        exception = aiohttp.ClientResponseError(None, None)
        self.mock_session.get.side_effect = exception
        self.assertIsNone(await ffz.getGlobalEmotes())

    async def test_broadcasterEmotes(self):
        data = json.loads(broadcasterEmotes.decode())
        self.mock_response.json.return_value = data
        self.assertEqual(await ffz.getBroadcasterEmotes('pokemonspeedrunstv'),
                         {18146: 'KevinSquirtle'})

    async def test_broadcasterEmotes_404(self):
        exception = aiohttp.ClientResponseError(None, None, code=404)
        self.mock_session.get.side_effect = exception
        self.assertEqual(await ffz.getBroadcasterEmotes('pokemonspeedrunstv'),
                         {})

    async def test_broadcasterEmotes_error(self):
        exception = aiohttp.ClientResponseError(None, None)
        self.mock_session.get.side_effect = exception
        self.assertIsNone(await ffz.getBroadcasterEmotes('pokemonspeedrunstv'))
