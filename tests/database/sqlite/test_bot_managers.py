from datetime import datetime
from tests.database.sqlite.test_database import TestSqlite
from tests.unittest.mock_class import TypeMatch


class TestSqlitePermittedUsers(TestSqlite):
    def setUp(self):
        super().setUp()
        self.execute(['''
CREATE TABLE bot_managers (
    twitchUser VARCHAR NOT NULL PRIMARY KEY
)''','''
CREATE TABLE bot_managers_log (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    twitchUser VARCHAR NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actionLog VARCHAR NOT NULL
)''','''
INSERT INTO bot_managers VALUES ('megotsthis')'''])

    def test_is_bot_manager_true(self):
        self.assertIs(self.database.isBotManager('megotsthis'), True)

    def test_is_bot_manager_false(self):
        self.assertIs(self.database.isBotManager('mebotsthis'), False)

    def test_add(self):
        self.assertIs(self.database.addBotManager('mebotsthis'), True)
        self.assertEqual(
            self.rows('SELECT * FROM bot_managers'),
            [('megotsthis',),
             ('mebotsthis',)])
        self.assertEqual(
            self.row('SELECT * FROM bot_managers_log'),
            (1, 'mebotsthis', TypeMatch(datetime), 'add'))

    def test_add_existing(self):
        self.assertIs(self.database.addBotManager('megotsthis'), False)
        self.assertIsNone(self.row('SELECT * FROM bot_managers_log'))

    def test_remove(self):
        self.assertIs(self.database.removeBotManager('mebotsthis'), False)

    def test_remove_existing(self):
        self.assertIs(self.database.removeBotManager('megotsthis'), True)
        self.assertIsNone(self.row('SELECT * FROM bot_managers'))
        self.assertEqual(
            self.row('SELECT * FROM bot_managers_log'),
            (1, 'megotsthis', TypeMatch(datetime), 'remove'))
