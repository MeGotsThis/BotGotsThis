import unittest
from http.client import HTTPResponse
from source.api import ffz
from urllib.error import HTTPError, URLError
from unittest.mock import MagicMock, Mock, patch


class TestApiFfz(unittest.TestCase):
    @patch('source.api.ffz.urlopen', autospec=True)
    def test_globalEmotes(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.return_value = mockResponse
        mockResponse.status = 200
        mockResponse.read = Mock(spec=HTTPResponse.read)
        mockResponse.read.return_value = b'''{
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
        self.assertEqual(ffz.getGlobalEmotes(), {3: 'BeanieHipster'})

    @patch('source.api.ffz.urlopen')
    def test_globalEmotes_404(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.side_effect = HTTPError(None, 404, None, None, None)
        self.assertEqual(ffz.getGlobalEmotes(), {})

    @patch('source.api.ffz.urlopen')
    def test_globalEmotes_error(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.side_effect = URLError(None)
        self.assertIsNone(ffz.getGlobalEmotes())

    @patch('source.api.ffz.urlopen')
    def test_broadcasterEmotes(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.return_value = mockResponse
        mockResponse.status = 200
        mockResponse.read = Mock(spec=HTTPResponse.read)
        mockResponse.read.return_value = b'''{
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
        self.assertEqual(ffz.getBroadcasterEmotes('pokemonspeedrunstv'), {18146: 'KevinSquirtle'})

    @patch('source.api.ffz.urlopen')
    def test_broadcasterEmotes_404(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.side_effect = HTTPError(None, 404, None, None, None)
        self.assertEqual(ffz.getBroadcasterEmotes('pokemonspeedrunstv'), {})

    @patch('source.api.ffz.urlopen')
    def test_broadcasterEmotes_error(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.side_effect = URLError(None)
        self.assertIsNone(ffz.getBroadcasterEmotes('pokemonspeedrunstv'))
