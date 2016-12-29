import math
from datetime import datetime, timedelta
from source.database.sqlite import AutoRepeatList, AutoRepeatMessage
from tests.database.sqlite.test_database import TestSqlite


class TestSqliteAutoRepeat(TestSqlite):
    def setUp(self):
        super().setUp()
        self.execute('''
CREATE TABLE auto_repeat (
    broadcaster VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    message VARCHAR NOT NULL,
    numLeft INTEGER,
    duration REAL NOT NULL,
    lastSent TIMESTAMP NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (broadcaster, name)
);
''')

    def test_empty(self):
        self.assertEqual(list(self.database.getAutoRepeatToSend()), [])

    def test_nothing_to_send(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.execute("INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
                     ('botgotsthis', '', 'Kappa', None, 5, dt, dt))
        self.assertEqual(list(self.database.getAutoRepeatToSend()), [])

    def test_something_to_send(self):
        self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 5,
              datetime.utcnow() - timedelta(minutes=5), datetime.utcnow()),
             ('botgotsthis', 'kappa', 'Kappa', None, 5,
              datetime.utcnow(), datetime.utcnow())
             ])
        self.assertEqual(list(self.database.getAutoRepeatToSend()),
                         [AutoRepeatMessage('botgotsthis', '', 'Kappa')])

    def test_something_to_send_decimal(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 0.1,
              dt - timedelta(seconds=6), dt),
             ('botgotsthis', 'kappa', 'Kappa', None, 5,
              dt - timedelta(seconds=5), dt)
             ])
        self.assertEqual(list(self.database.getAutoRepeatToSend()),
                         [AutoRepeatMessage('botgotsthis', '', 'Kappa')])

    def test_something_to_send_count(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', 10, 5,
              dt - timedelta(minutes=5), dt),
             ('botgotsthis', 'kappa', 'Kappa', 10, 5,
              dt, dt)
             ])
        self.assertEqual(list(self.database.getAutoRepeatToSend()),
                         [AutoRepeatMessage('botgotsthis', '', 'Kappa')])

    def test_something_to_send_multiple(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', 10, 5,
              dt - timedelta(minutes=5), dt),
             ('botgotsthis', 'kappa', 'Kappa', None, 5,
              dt - timedelta(minutes=5), dt)
             ])
        self.assertEqual(list(self.database.getAutoRepeatToSend()),
                         [AutoRepeatMessage('botgotsthis', '', 'Kappa'),
                          AutoRepeatMessage('botgotsthis', 'kappa', 'Kappa')])

    def test_list_empty(self):
        self.assertEqual(list(self.database.listAutoRepeat('botgotsthis')),
                         [])

    def test_list(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 0.1, dt, dt),
             ('botgotsthis', 'kappa', 'Kappa', 10, 5, dt, dt)
             ])
        self.assertEqual(list(self.database.listAutoRepeat('botgotsthis')),
                         [AutoRepeatList('', 'Kappa', None, 0.1, dt),
                          AutoRepeatList('kappa', 'Kappa', 10, 5, dt)])

    def test_clear_empty(self):
        self.assertFalse(self.database.clearAutoRepeat('botgotsthis'))
        self.assertEqual(self.rows('SELECT * FROM auto_repeat'), [])
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 0.1, dt, dt),
             ('botgotsthis', 'kappa', 'Kappa', 10, 5, dt, dt)
             ])
        self.assertFalse(self.database.clearAutoRepeat('megotsthis'))
        self.assertEqual(
            self.rows('SELECT * FROM auto_repeat'),
            [('botgotsthis', '', 'Kappa', None, 0.1, dt, dt),
             ('botgotsthis', 'kappa', 'Kappa', 10, 5, dt, dt),
             ])

    def test_clear(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 0.1, dt, dt),
             ('botgotsthis', 'kappa', 'Kappa', 10, 5, dt, dt)
             ])
        self.assertTrue(self.database.clearAutoRepeat('botgotsthis'))
        self.assertEqual(self.rows('SELECT * FROM auto_repeat'), [])

    def test_message_sent(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 0.1,
              dt - timedelta(seconds=6), dt),
             ('botgotsthis', 'kappa', 'Kappa', 10, 5,
              dt - timedelta(minutes=5), dt),
             ('botgotsthis', ':)', ':)', 1, 5,
              dt - timedelta(minutes=5), dt),
             ('botgotsthis', ':(', ':(', 0, 5,
              dt - timedelta(minutes=5), dt),
             ('botgotsthis', 'vohiyo', 'VoHiYo', 10, 5, dt, dt),
             ('botgotsthis', 'keepo', 'Keepo', None, 5, dt, dt),
             ])
        self.assertTrue(self.database.sentAutoRepeat('botgotsthis', ''))
        self.assertTrue(self.database.sentAutoRepeat('botgotsthis', 'kappa'))
        self.assertTrue(self.database.sentAutoRepeat('botgotsthis', ':)'))
        self.assertTrue(self.database.sentAutoRepeat('botgotsthis', ':('))
        self.maxDiff = None
        self.assertEqual(
            self.rows('SELECT * FROM auto_repeat'),
            [('botgotsthis', '', 'Kappa', None, 0.1, dt, dt),
             ('botgotsthis', 'kappa', 'Kappa', 9, 5, dt, dt),
             ('botgotsthis', 'vohiyo', 'VoHiYo', 10, 5, dt, dt),
             ('botgotsthis', 'keepo', 'Keepo', None, 5, dt, dt),
             ])

    def test_set_auto_repeat(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.assertTrue(
            self.database.setAutoRepeat('botgotsthis', '', 'Kappa', None, 5))
        self.assertEqual(
            self.rows('SELECT * FROM auto_repeat'),
            [('botgotsthis', '', 'Kappa', None, 5,
              dt - timedelta(minutes=5), dt),
             ])

    def test_set_auto_repeat_multiple(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.assertTrue(
            self.database.setAutoRepeat('botgotsthis', '', 'Kappa', None, 5))
        self.assertTrue(
            self.database.setAutoRepeat('botgotsthis', '', 'Keepo', None, 5))
        self.assertEqual(
            self.rows('SELECT * FROM auto_repeat'),
            [('botgotsthis', '', 'Keepo', None, 5,
              dt - timedelta(minutes=5), dt),
             ])

    def test_set_auto_repeat_multiple_names(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.assertTrue(
            self.database.setAutoRepeat('botgotsthis', '', 'Kappa', None, 5))
        self.assertTrue(
            self.database.setAutoRepeat(
                'botgotsthis', 'Kappa', 'Keepo', None, 5))
        self.assertEqual(
            self.rows('SELECT * FROM auto_repeat'),
            [('botgotsthis', '', 'Kappa', None, 5,
              dt - timedelta(minutes=5), dt),
             ('botgotsthis', 'Kappa', 'Keepo', None, 5,
              dt - timedelta(minutes=5), dt),
             ])

    def test_delete(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 5, dt, dt),
             ('botgotsthis', 'kappa', 'Kappa', None, 5, dt, dt)
             ])
        self.assertTrue(self.database.removeAutoRepeat('botgotsthis', ''))
        self.assertEqual(
            self.rows('SELECT * FROM auto_repeat'),
            [('botgotsthis', 'kappa', 'Kappa', None, 5, dt, dt),
             ])

    def test_delete_not_existing(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.assertFalse(self.database.removeAutoRepeat('botgotsthis', ''))
        self.assertEqual(self.rows('SELECT * FROM auto_repeat'), [])
