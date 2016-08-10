from datetime import datetime
from tests.database.sqlite.test_database import TestSqlite
from tests.unittest.mock_class import TypeMatch


class TestSqliteTimeout(TestSqlite):
    def setUp(self):
        super().setUp()
        self.database._attachTimeout(self.cursor)
        self.execute('''
CREATE TABLE timeout.timeout_logs (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    theTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    broadcaster VARCHAR NOT NULL,
    twitchUser VARCHAR NOT NULL,
    fromUser VARCHAR,
    module VARCHAR NOT NULL,
    level INTEGER,
    length INTEGER,
    message VARCHAR NULL,
    reason VARCHAR
)''')

    def test_record(self):
        self.database.recordTimeout(
            'botgotsthis', 'botgotsthis', None, 'tests', None, None, None,
            None)
        self.assertEqual(
            self.row('SELECT * FROM timeout.timeout_logs'),
            (1, TypeMatch(datetime), 'botgotsthis', 'botgotsthis', None, 'tests', None, None,
             None, None))

    def test_record2(self):
        self.database.recordTimeout(
            'botgotsthis', 'megotsthis', 'mebotsthis', 'tests', 0, 3600,
            'Kappa', 'KappaHD')
        self.assertEqual(
            self.row('SELECT * FROM timeout.timeout_logs'),
            (1, TypeMatch(datetime), 'botgotsthis', 'megotsthis', 'mebotsthis', 'tests', 0,
             3600, 'Kappa', 'KappaHD'))
