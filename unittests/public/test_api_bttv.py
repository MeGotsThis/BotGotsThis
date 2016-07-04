import unittest
from http.client import HTTPResponse
from source.api import bttv
from urllib.error import HTTPError, URLError
from unittest.mock import MagicMock, Mock, patch


class TestApiFfz(unittest.TestCase):
    @patch('source.api.bttv.urlopen', autospec=True)
    def test_globalEmotes(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.return_value = mockResponse
        mockResponse.status = 200
        mockResponse.read = Mock(spec=HTTPResponse.read)
        mockResponse.read.return_value = b'''{
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
        self.assertEqual(bttv.getGlobalEmotes(), {'54fa925e01e468494b85b54d': 'OhMyGoodness'})

    @patch('source.api.bttv.urlopen')
    def test_globalEmotes_404(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.side_effect = HTTPError(None, 404, None, None, None)
        self.assertEqual(bttv.getGlobalEmotes(), {})

    @patch('source.api.bttv.urlopen')
    def test_globalEmotes_error(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.side_effect = URLError(None)
        self.assertIsNone(bttv.getGlobalEmotes())

    @patch('source.api.bttv.urlopen')
    def test_broadcasterEmotes(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.return_value = mockResponse
        mockResponse.status = 200
        mockResponse.read = Mock(spec=HTTPResponse.read)
        mockResponse.read.return_value = b'''{
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
        self.assertEqual(bttv.getBroadcasterEmotes('pokemonspeedrunstv'), {'554da1a289d53f2d12781907': '(ditto)'})

    @patch('source.api.bttv.urlopen')
    def test_broadcasterEmotes_404(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.side_effect = HTTPError(None, 404, None, None, None)
        self.assertEqual(bttv.getBroadcasterEmotes('pokemonspeedrunstv'), {})

    @patch('source.api.bttv.urlopen')
    def test_broadcasterEmotes_error(self, mock_urlopen):
        mockResponse = MagicMock(spec=HTTPResponse)
        mock_urlopen.return_value = mockResponse
        mockResponse.__enter__.side_effect = URLError(None)
        self.assertIsNone(bttv.getBroadcasterEmotes('pokemonspeedrunstv'))
