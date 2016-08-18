import urllib.error
import re
from http.client import HTTPResponse
from unittest.mock import ANY, Mock, patch

from source.data.message import Message
from source.public.custom import url
from tests.unittest.base_custom import TestCustomField


class TestCustomUrl(TestCustomField):
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

    @patch('source.public.custom.url.field_replace')
    def test_field(self, mock_replace):
        mock_replace.return_value = 'PogChamp'
        self.args = self.args._replace(param='http://localhost/{query}')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/PogChamp', timeout=1)


class TestFieldReplace(TestCustomField):
    def setUp(self):
        super().setUp()

        patcher = patch('source.public.custom.url.fieldUrl')
        self.addCleanup(patcher.stop)
        self.mock_fieldUrl = patcher.start()

        patcher = patch('lists.custom')
        self.addCleanup(patcher.stop)
        self.mock_list = patcher.start()
        self.mock_list.fields = [self.mock_fieldUrl]

        self.match = re.match(r'(.*)', 'Kappa')

    def test(self):
        self.assertEqual(url.field_replace(self.args, self.match), '')
        self.assertFalse(self.mock_fieldUrl.called)

    def test_something(self):
        self.mock_list.fields.append(Mock(return_value='Kappa'))
        self.assertEqual(url.field_replace(self.args, self.match), 'Kappa')
        self.assertFalse(self.mock_fieldUrl.called)

    def test_none(self):
        self.mock_list.fields.append(Mock(return_value=None))
        self.assertEqual(url.field_replace(self.args, self.match), '')
        self.assertFalse(self.mock_fieldUrl.called)
