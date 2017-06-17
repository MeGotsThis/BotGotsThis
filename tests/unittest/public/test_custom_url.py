import re

from asynctest.mock import CoroutineMock, Mock, patch

from source.data.message import Message
from tests.unittest.base_custom import TestCustomField

# Needs to be imported last
from source.public.custom import url


class TestCustomUrl(TestCustomField):
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

    async def test(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.args = self.args._replace(field='')
        self.assertIsNone(await url.fieldUrl(self.args))

    async def fail_test_url(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    async def fail_test_caps(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.args = self.args._replace(field='URL')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    async def fail_test_default(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.args = self.args._replace(prefix='[', suffix=']')
        self.request.status = 404
        self.assertEqual(url.fieldUrl(self.args), '')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    async def fail_test_exception(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.mock_urlopen.side_effect = Exception
        self.assertEqual(url.fieldUrl(self.args), '')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    async def fail_test_prefix(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.args = self.args._replace(prefix='[')
        self.assertEqual(url.fieldUrl(self.args), '[Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    async def fail_test_prefix_blank(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.args = self.args._replace(prefix='')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    async def fail_test_suffix(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.args = self.args._replace(suffix=']')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa]')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    async def fail_test_suffix_blank(self):
        # TODO: Fix when asynctest is updated with magic mock
        self.args = self.args._replace(suffix='')
        self.assertEqual(url.fieldUrl(self.args), 'Kappa')
        self.mock_urlopen.assert_called_once_with(
            'http://localhost/', timeout=1)

    @patch('source.public.custom.url.field_replace')
    async def fail_test_field(self, mock_replace):
        # TODO: Fix when asynctest is updated with magic mock
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

    async def test(self):
        self.assertEqual(await url.field_replace(self.args, self.match), '')
        self.assertFalse(self.mock_fieldUrl.called)

    async def test_something(self):
        self.mock_list.fields.append(CoroutineMock(return_value='Kappa'))
        self.assertEqual(await url.field_replace(self.args, self.match),
                         'Kappa')
        self.assertFalse(self.mock_fieldUrl.called)

    async def test_none(self):
        self.mock_list.fields.append(CoroutineMock(return_value=None))
        self.assertEqual(await url.field_replace(self.args, self.match), '')
        self.assertFalse(self.mock_fieldUrl.called)
