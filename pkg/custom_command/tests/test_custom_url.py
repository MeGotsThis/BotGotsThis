import re

import aiohttp

from asynctest.mock import CoroutineMock, MagicMock, patch

from lib.data.message import Message
from tests.unittest.base_custom import TestCustomField

# Needs to be imported last
from ..custom import url


class TestCustomCommandCustomUrl(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='url',
                                       nick='megotsthis',
                                       message=Message('a query'),
                                       param='http://localhost/')

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.customMessageUrlTimeout = 1

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

    async def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(await url.fieldUrl(self.args))
        self.assertFalse(self.mock_clientsession.called)
        self.assertFalse(self.mock_session.get.called)
        self.assertFalse(self.mock_session.get.called)

    async def test_url(self):
        self.assertEqual(await url.fieldUrl(self.args), 'Kappa')
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://localhost/', timeout=1)
        self.assertTrue(self.mock_session.get.called)

    async def test_caps(self):
        self.args = self.args._replace(field='URL')
        self.assertEqual(await url.fieldUrl(self.args), 'Kappa')
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://localhost/', timeout=1)
        self.assertTrue(self.mock_session.get.called)

    async def test_default(self):
        self.args = self.args._replace(prefix='[', suffix=']')
        self.mock_response.status = 404
        self.assertEqual(await url.fieldUrl(self.args), '')
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://localhost/', timeout=1)
        self.assertTrue(self.mock_session.get.called)

    async def test_exception(self):
        self.mock_session.get.side_effect = aiohttp.ClientError
        self.assertEqual(await url.fieldUrl(self.args), '')
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://localhost/', timeout=1)
        self.assertTrue(self.mock_session.get.called)

    async def test_prefix(self):
        self.args = self.args._replace(prefix='[')
        self.assertEqual(await url.fieldUrl(self.args), '[Kappa')
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://localhost/', timeout=1)
        self.assertTrue(self.mock_session.get.called)

    async def test_prefix_blank(self):
        self.args = self.args._replace(prefix='')
        self.assertEqual(await url.fieldUrl(self.args), 'Kappa')
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://localhost/', timeout=1)
        self.assertTrue(self.mock_session.get.called)

    async def test_suffix(self):
        self.args = self.args._replace(suffix=']')
        self.assertEqual(await url.fieldUrl(self.args), 'Kappa]')
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://localhost/', timeout=1)
        self.assertTrue(self.mock_session.get.called)

    async def test_suffix_blank(self):
        self.args = self.args._replace(suffix='')
        self.assertEqual(await url.fieldUrl(self.args), 'Kappa')
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://localhost/', timeout=1)
        self.assertTrue(self.mock_session.get.called)

    @patch('pkg.custom_command.custom.url.field_replace')
    async def test_field(self, mock_replace):
        mock_replace.side_effect = ['PogChamp', 'FrankerZ']
        self.args = self.args._replace(param='http://localhost/{user}/{query}')
        self.assertEqual(await url.fieldUrl(self.args), 'Kappa')
        self.assertTrue(self.mock_clientsession.called)
        self.mock_session.get.assert_called_once_with(
            'http://localhost/FrankerZ/PogChamp', timeout=1)
        self.assertTrue(self.mock_session.get.called)


class TestCustomCommandFieldReplace(TestCustomField):
    def setUp(self):
        super().setUp()

        patcher = patch('pkg.custom_command.custom.url.fieldUrl')
        self.addCleanup(patcher.stop)
        self.mock_fieldUrl = patcher.start()

        patcher = patch('lib.items.custom')
        self.addCleanup(patcher.stop)
        self.mock_list = patcher.start()
        self.mock_list.fields.return_value = [self.mock_fieldUrl]

        self.match = re.match(r'(.*)', 'Kappa')

    async def test(self):
        self.assertEqual(await url.field_replace(self.args, self.match), '')
        self.assertFalse(self.mock_fieldUrl.called)

    async def test_something(self):
        self.mock_list.fields.return_value.append(
            CoroutineMock(return_value='Kappa'))
        self.assertEqual(await url.field_replace(self.args, self.match),
                         'Kappa')
        self.assertFalse(self.mock_fieldUrl.called)

    async def test_none(self):
        self.mock_list.fields.return_value.append(
            CoroutineMock(return_value=None))
        self.assertEqual(await url.field_replace(self.args, self.match), '')
        self.assertFalse(self.mock_fieldUrl.called)
