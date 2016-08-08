import unittest
from datetime import datetime, timedelta
from source import api
from unittest.mock import patch


class TestApi(unittest.TestCase):
    @patch('bot.utils.now', autospec=True)
    @patch('bot.globals', autospec=True)
    def test_cache(self, mock_globals, mock_now):
        basenow = datetime(2000, 1, 1)
        data = {}
        mock_now.return_value = basenow
        mock_globals.globalSessionData = data
        i = 0

        @api.cache('Kappa', timedelta(seconds=60))
        def d():
            nonlocal i
            i += 1
            return i

        self.assertEqual(d(), 1)
        self.assertIn('Kappa', mock_globals.globalSessionData)
        self.assertIn(((), ()), mock_globals.globalSessionData['Kappa'])
        self.assertEqual(
            basenow, mock_globals.globalSessionData['Kappa'][(), ()][0])
        self.assertEqual(mock_globals.globalSessionData['Kappa'][(), ()][1], 1)
        mock_now.return_value = basenow + timedelta(seconds=30)
        self.assertEqual(d(), 1)
        self.assertEqual(
            basenow, mock_globals.globalSessionData['Kappa'][(), ()][0])
        self.assertEqual(mock_globals.globalSessionData['Kappa'][(), ()][1], 1)
        mock_now.return_value = basenow + timedelta(seconds=60)
        self.assertEqual(d(), 2)
        self.assertEqual(
            basenow + timedelta(seconds=60),
            mock_globals.globalSessionData['Kappa'][(), ()][0])
        self.assertEqual(mock_globals.globalSessionData['Kappa'][(), ()][1], 2)

    @patch('bot.utils.now', autospec=True)
    @patch('bot.globals', autospec=True)
    def test_cache_except(self, mock_globals, mock_now):
        mock_now.return_value = datetime(2000, 1, 1)
        mock_globals.globalSessionData = {}

        @api.cache('Kappa', timedelta(seconds=60))
        def d():
            raise ConnectionError()

        self.assertEqual(d(), None)
