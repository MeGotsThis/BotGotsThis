import math
from source.database.sqlite import AutoJoinChannel
from tests.database.sqlite.test_database import TestSqlite


class TestSqliteAutoJoin(TestSqlite):
    def setUp(self):
        super().setUp()
        self.execute('''
CREATE TABLE auto_join (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    priority INT NOT NULL DEFAULT 0,
    cluster VARCHAR NOT NULL DEFAULT 'main'
)''')

    def test_chats_empty(self):
        self.assertEqual(list(self.database.getAutoJoinsChats()), [])

    def test_chat(self):
        self.execute("INSERT INTO auto_join VALUES (?, ?, ?)",
                     ('botgotsthis', 0, 'main'))
        self.assertEqual(list(self.database.getAutoJoinsChats()),
                         [AutoJoinChannel('botgotsthis', 0, 'main')])

    def test_chats(self):
        self.executemany("INSERT INTO auto_join VALUES (?, ?, ?)",
                         [('botgotsthis', 0, 'main'),
                          ('megotsthis', -1, 'twitch'),
                          ('mebotsthis', 1, 'aws')])
        self.assertEqual(list(self.database.getAutoJoinsChats()),
                         [AutoJoinChannel('megotsthis', -1, 'twitch'),
                          AutoJoinChannel('botgotsthis', 0, 'main'),
                          AutoJoinChannel('mebotsthis', 1, 'aws')])

    def test_priority_not_existing(self):
        self.assertEqual(self.database.getAutoJoinsPriority('botgotsthis'),
                         math.inf)

    def test_priority(self):
        self.execute("INSERT INTO auto_join VALUES ('botgotsthis', 0, 'main')")
        self.assertEqual(self.database.getAutoJoinsPriority('botgotsthis'),
                         0)

    def test_save(self):
        self.assertIs(self.database.saveAutoJoin('botgotsthis', 0, 'twitch'),
                      True)
        self.assertEqual(self.row('SELECT * FROM auto_join'),
                         ('botgotsthis', 0, 'twitch'))

    def test_save_existing(self):
        self.execute("INSERT INTO auto_join VALUES (?, ?, ?)",
                     ('botgotsthis', -1, 'main'))
        self.assertIs(self.database.saveAutoJoin('botgotsthis', 0, 'twitch'),
                      False)
        self.assertEqual(self.row('SELECT * FROM auto_join'),
                         ('botgotsthis', -1, 'main'))

    def test_discard(self):
        self.execute("INSERT INTO auto_join VALUES (?, ?, ?)",
                     ('botgotsthis', 0, 'main'))
        self.assertIs(self.database.discardAutoJoin('botgotsthis'), True)
        self.assertIsNone(self.row('SELECT * FROM auto_join'))

    def test_discard_not_existing(self):
        self.assertIs(self.database.discardAutoJoin('botgotsthis'), False)
        self.assertIsNone(self.row('SELECT * FROM auto_join'))

    def test_save_priority(self):
        self.execute("INSERT INTO auto_join VALUES (?, ?, ?)",
                     ('botgotsthis', 0, 'main'))
        self.assertIs(self.database.setAutoJoinPriority('botgotsthis', -1),
                      True)
        self.assertEqual(self.row('SELECT * FROM auto_join'),
                         ('botgotsthis', -1, 'main'))

    def test_save_priority_not_existing(self):
        self.assertIs(self.database.setAutoJoinPriority('botgotsthis', 0),
                      False)
        self.assertIsNone(self.row('SELECT * FROM auto_join'))

    def test_save_server(self):
        self.execute("INSERT INTO auto_join VALUES (?, ?, ?)",
                     ('botgotsthis', 0, 'main'))
        self.assertIs(self.database.setAutoJoinServer('botgotsthis', 'twitch'),
                      True)
        self.assertEqual(self.row('SELECT * FROM auto_join'),
                         ('botgotsthis', 0, 'twitch'))

    def test_save_server_not_existing(self):
        self.assertIs(self.database.setAutoJoinServer('botgotsthis', 'twitch'),
                      False)
        self.assertIsNone(self.row('SELECT * FROM auto_join'))
