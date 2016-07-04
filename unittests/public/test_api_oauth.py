import unittest
from source.api import oauth
from source.database import DatabaseBase
from unittest.mock import MagicMock, Mock, patch

class TestApiOAuth(unittest.TestCase):
    def test_token(self):
        mock_database = Mock(spec=DatabaseBase)
        mock_database.getOAuthToken.return_value = '0123456789abcedf'
        self.assertEqual(oauth.token('botgotsthis', database=mock_database), '0123456789abcedf')
        mock_database.getOAuthToken.assert_called_once_with('botgotsthis')

    def test_token_none(self):
        mock_database = Mock(spec=DatabaseBase)
        mock_database.getOAuthToken.return_value = '0123456789abcedf'
        self.assertRaises(TypeError, oauth.token, None, database=mock_database)

    @patch('source.api.oauth.getDatabase')
    def test_token_database_none(self, mock_getDatabase):
        mock_getDatabase.return_value = MagicMock()
        mock_database = Mock(spec=DatabaseBase)
        mock_database.getOAuthToken.return_value = '0123456789abcedf'
        mock_getDatabase.return_value.__enter__.return_value = mock_database
        self.assertEqual(oauth.token('botgotsthis'), '0123456789abcedf')
        mock_database.getOAuthToken.assert_called_once_with('botgotsthis')

    def test_token_database_str(self):
        self.assertRaises(TypeError, oauth.token, 'botgotsthis', database='')
