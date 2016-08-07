import os
from tests.database.sqlite.test_database import TestSqlite


class TestSqliteFeatures(TestSqlite):
    def setUp(self):
        super().setUp()
        self.execute('''
CREATE TABLE chat_features (
    broadcaster VARCHAR NOT NULL,
    feature VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, feature)
)''')

    def test_has(self):
        self.assertIs(self.database.hasFeature('botgotsthis', 'feature'),
                      False)

    def test_has_existing(self):
        self.execute('INSERT INTO chat_features VALUES (?, ?)',
                     ('botgotsthis', 'feature'))
        self.assertIs(self.database.hasFeature('botgotsthis', 'feature'), True)

    def test_add(self):
        self.assertIs(self.database.addFeature('botgotsthis', 'feature'), True)
        self.assertEqual(self.row('SELECT * FROM chat_features'),
                         ('botgotsthis', 'feature'))

    def test_add_existing(self):
        self.execute('INSERT INTO chat_features VALUES (?, ?)',
                     ('botgotsthis', 'feature'))
        self.assertIs(self.database.addFeature('botgotsthis', 'feature'),
                      False)

    def test_remove(self):
        self.assertIs(self.database.removeFeature('botgotsthis', 'feature'),
                      False)

    def test_remove_existing(self):
        self.execute('INSERT INTO chat_features VALUES (?, ?)',
                     ('botgotsthis', 'feature'))
        self.assertIs(self.database.removeFeature('botgotsthis', 'feature'),
                      True)
        self.assertIsNone(self.row('SELECT * FROM chat_features'))
