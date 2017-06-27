import asynctest
from datetime import datetime, timedelta
from source.api import cache
from asynctest.mock import patch


class TestApi(asynctest.TestCase):
    @patch('bot.utils.now', autospec=True)
    @patch('bot.globals', autospec=True)
    async def test_cache(self, mock_globals, mock_now):
        basenow = datetime(2000, 1, 1)
        data = {}
        mock_now.return_value = basenow
        mock_globals.globalSessionData = data
        i = 0

        @cache.cache('Kappa', timedelta(seconds=60))
        async def d():
            nonlocal i
            i += 1
            return i

        self.assertEqual(await d(), 1)
        self.assertIn('Kappa', mock_globals.globalSessionData)
        self.assertIn(((), ()), mock_globals.globalSessionData['Kappa'])
        self.assertEqual(
            basenow, mock_globals.globalSessionData['Kappa'][(), ()][0])
        self.assertEqual(mock_globals.globalSessionData['Kappa'][(), ()][1], 1)
        mock_now.return_value = basenow + timedelta(seconds=30)
        self.assertEqual(await d(), 1)
        self.assertEqual(
            basenow, mock_globals.globalSessionData['Kappa'][(), ()][0])
        self.assertEqual(mock_globals.globalSessionData['Kappa'][(), ()][1], 1)
        mock_now.return_value = basenow + timedelta(seconds=60)
        self.assertEqual(await d(), 2)
        self.assertEqual(
            basenow + timedelta(seconds=60),
            mock_globals.globalSessionData['Kappa'][(), ()][0])
        self.assertEqual(mock_globals.globalSessionData['Kappa'][(), ()][1], 2)

    @patch('bot.utils.now', autospec=True)
    @patch('bot.globals', autospec=True)
    async def test_cache_except(self, mock_globals, mock_now):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_globals.globalSessionData = {}

        @cache.cache('Kappa', timedelta(seconds=60))
        async def d():
            raise ConnectionError()

        self.assertEqual(await d(), None)
