import os
from tests.database.sqlite.test_database import TestSqlite


class TestSqliteOAuth(TestSqlite):
    def setUp(self):
        super().setUp()
        self.database._attachOauth(self.cursor)
        self.execute('''
CREATE TABLE oauth.oauth_tokens (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    token VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE
)''')

    def test_get_empty(self):
        self.assertIsNone(self.database.getOAuthToken('botgotsthis'))

    def test_get_existing(self):
        self.execute('INSERT INTO oauth.oauth_tokens VALUES (?, ?)',
                     ('botgotsthis', '0123456789ABCDEF'))
        self.assertEqual(self.database.getOAuthToken('botgotsthis'),
                         '0123456789ABCDEF')

    def test_save(self):
        self.database.saveBroadcasterToken('botgotsthis', '0123456789ABCDEF')
        self.assertEqual(self.row('SELECT * FROM oauth.oauth_tokens'),
                         ('botgotsthis', '0123456789ABCDEF'))

    def test_save_existing(self):
        self.execute('INSERT INTO oauth.oauth_tokens VALUES (?, ?)',
                     ('botgotsthis', '0123456789ABCDEF'))
        self.database.saveBroadcasterToken('botgotsthis', 'FEDCBA9876543210')
        self.assertEqual(self.row('SELECT * FROM oauth.oauth_tokens'),
                         ('botgotsthis', 'FEDCBA9876543210'))
