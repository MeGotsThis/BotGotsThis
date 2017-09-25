import aiohttp

from asynctest.mock import MagicMock, patch

from tests.unittest.base_custom import TestCustomField
from lib.data.message import Message
from ...custom import url


class TestCustomUrl(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='url',
                                       nick='megotsthis',
                                       message=Message('a query'),
                                       param='http://localhost/')

        self.mock_response = MagicMock(spec=aiohttp.ClientResponse)
        self.mock_response.__aenter__.return_value = self.mock_response
        self.mock_response.__aexit__.return_value = False
        self.mock_response.status = 200
        self.mock_response.text.return_value = 'Kappa'

        self.mock_session = MagicMock(spec=aiohttp.ClientSession)
        self.mock_session.__aenter__.return_value = self.mock_session
        self.mock_session.__aexit__.return_value = False
        self.mock_session.get.return_value = self.mock_response

        patcher = patch('aiohttp.ClientSession')
        self.addCleanup(patcher.stop)
        self.mock_clientsession = patcher.start()
        self.mock_clientsession.return_value = self.mock_session

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.customMessageUrlTimeout = 1

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.pkgs = ['custom_command']

    async def test_query(self):
        self.args = self.args._replace(param='http://localhost/{query}')
        self.assertEqual(await url.fieldUrl(self.args), 'Kappa')
        self.mock_session.get.assert_called_once_with(
            'http://localhost/query', timeout=1)

    async def test_user(self):
        self.args = self.args._replace(param='http://localhost/{user}',
                                       nick='megotsthis')
        self.assertEqual(await url.fieldUrl(self.args), 'Kappa')
        self.mock_session.get.assert_called_once_with(
            'http://localhost/megotsthis', timeout=1)

    async def test_nick(self):
        self.args = self.args._replace(param='http://localhost/{nick}',
                                       nick='megotsthis')
        self.assertEqual(await url.fieldUrl(self.args), 'Kappa')
        self.mock_session.get.assert_called_once_with(
            'http://localhost/megotsthis', timeout=1)

    async def test_broadcaster(self):
        self.args = self.args._replace(param='http://localhost/{broadcaster}')
        self.assertEqual(await url.fieldUrl(self.args), 'Kappa')
        self.mock_session.get.assert_called_once_with(
            'http://localhost/botgotsthis', timeout=1)

    async def test_streamer(self):
        self.args = self.args._replace(param='http://localhost/{streamer}')
        self.assertEqual(await url.fieldUrl(self.args), 'Kappa')
        self.mock_session.get.assert_called_once_with(
            'http://localhost/botgotsthis', timeout=1)
