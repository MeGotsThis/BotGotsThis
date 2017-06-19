import unittest
from source.api import oauth
from source.database import DatabaseOAuth
from unittest.mock import MagicMock, Mock, patch


class TestApiOAuth(unittest.TestCase):
    @patch('source.database.get_database')
    def fail_test_token(self, mock_getDatabase):
        mock_getDatabase.return_value = MagicMock()
        mock_database = Mock(spec=DatabaseOAuth)
        mock_database.getOAuthToken.return_value = '0123456789abcedf'
        mock_getDatabase.return_value.__enter__.return_value = mock_database
        self.assertEqual(oauth.token('botgotsthis'), '0123456789abcedf')
        mock_database.getOAuthToken.assert_called_once_with('botgotsthis')
