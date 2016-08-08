import urllib.error
from http.client import HTTPResponse
from source.data.message import Message
from source.public.custom import url
from tests.unittest.public.test_custom import TestCustomField
from unittest.mock import Mock, patch


class TestCustomQuery(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='url',
                                       nick='megotsthis',
                                       message=Message('a query'),
                                       param='http://localhost/')

        patcher = patch('source.public.custom.url.urllib.request.urlopen',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_urlopen = patcher.start()
        self.request = Mock(spec=HTTPResponse)
        self.mock_urlopen.return_value.__enter__.return_value = self.request
        self.request.status = 200
        self.request.read.return_value = b'Kappa'

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.customMessageUrlTimeout = 1

    def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(url.fieldUrl(self.args))
        self.assertFalse(self.mock_urlopen.called)

    def test_url(self):
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    def test_caps(self):
        self.args = self.args._replace(field='URL')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    def test_default(self):
        self.args = self.args._replace(prefix='[', suffix=']')
        self.request.status = 404
        self.assertEqual(url.fieldUrl(self.args), '')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    def test_exception(self):
        self.mock_urlopen.side_effect = urllib.error.URLError(None)
        self.assertEqual(url.fieldUrl(self.args), '')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    def test_prefix(self):
        self.args = self.args._replace(prefix='[')
        self.assertEqual(url.fieldUrl(self.args), '[Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    def test_prefix_blank(self):
        self.args = self.args._replace(prefix='')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    def test_suffix(self):
        self.args = self.args._replace(suffix=']')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa]')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    def test_suffix_blank(self):
        self.args = self.args._replace(suffix='')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    def test_query(self):
        self.args = self.args._replace(param='http://localhost/{query}')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/query', timeout=1)

    def test_user(self):
        self.args = self.args._replace(param='http://localhost/{user}',
                                       nick='megotsthis')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/megotsthis', timeout=1)

    def test_nick(self):
        self.args = self.args._replace(param='http://localhost/{nick}',
                                       nick='megotsthis')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/megotsthis', timeout=1)

    def test_broadcaster(self):
        self.args = self.args._replace(param='http://localhost/{broadcaster}')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/botgotsthis', timeout=1)

    def test_streamer(self):
        self.args = self.args._replace(param='http://localhost/{streamer}')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/botgotsthis', timeout=1)
