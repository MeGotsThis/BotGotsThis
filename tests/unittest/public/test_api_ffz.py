import unittest
from http.client import HTTPResponse
from source.api import ffz
from urllib.error import HTTPError, URLError
from unittest.mock import MagicMock, Mock, patch

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


class TestApiFfz(unittest.TestCase):
    @patch('urllib.request.urlopen', autospec=True)
    async def fail_test_globalEmotes(self, mock_urlopen):
        # TODO: Fix when asynctest is updated with magic mock
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.return_value = mockResponse
        mockResponse.status = 200
        mockResponse.read = Mock(spec=HTTPResponse.read)
        mockResponse.read.return_value = globalEmotes
        self.assertEqual(await ffz.getGlobalEmotes(), {3: 'BeanieHipster'})

    @patch('urllib.request.urlopen')
    async def fail_test_globalEmotes_404(self, mock_urlopen):
        # TODO: Fix when asynctest is updated with magic mock
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.side_effect = HTTPError(None, 404, None, None, None)
        self.assertEqual(await ffz.getGlobalEmotes(), {})

    @patch('urllib.request.urlopen')
    async def fail_test_globalEmotes_error(self, mock_urlopen):
        # TODO: Fix when asynctest is updated with magic mock
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.side_effect = URLError(None)
        self.assertIsNone(await ffz.getGlobalEmotes())

    @patch('urllib.request.urlopen')
    def test_broadcasterEmotes(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.return_value = mockResponse
        mockResponse.status = 200
        mockResponse.read = Mock(spec=HTTPResponse.read)
        mockResponse.read.return_value = broadcasterEmotes
        self.assertEqual(ffz.getBroadcasterEmotes('pokemonspeedrunstv'), {18146: 'KevinSquirtle'})

    @patch('urllib.request.urlopen')
    def test_broadcasterEmotes_404(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.side_effect = HTTPError(None, 404, None, None, None)
        self.assertEqual(ffz.getBroadcasterEmotes('pokemonspeedrunstv'), {})

    @patch('urllib.request.urlopen')
    def test_broadcasterEmotes_error(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.side_effect = URLError(None)
        self.assertIsNone(ffz.getBroadcasterEmotes('pokemonspeedrunstv'))
