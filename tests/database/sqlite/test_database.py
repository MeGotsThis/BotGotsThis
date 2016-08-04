import unittest
from collections.abc import Iterable
from source.database.sqlite import SQLiteDatabase


class TestSqlite(unittest.TestCase):
    def setUp(self):
        ini = {
            'file': ':memory:',
            'oauth': ':memory:',
            'timeoutlog': ':memory:',
            }
        self.database = SQLiteDatabase(ini)
        self.database.connect()
        self.cursor = self.database.connection.cursor()

    def tearDown(self):
        self.cursor.close()
        self.database.close()

    def execute(self, query, params=(), *, commit=True):
        if isinstance(query, str):
            self.cursor.execute(query, params)
        elif isinstance(query, Iterable):
            for q, p in zip(query, params):
                self.cursor.execute(q, p)
        else:
            raise TypeError()
        if commit:
            self.database.connection.commit()

    def executemany(self, query, params=(), *, commit=True):
        self.cursor.executemany(query, params)
        if commit:
            self.database.connection.commit()

    def value(self, query, params=()):
        self.cursor.execute(query, params)
        return (self.cursor.fetchone() or [None])[0]

    def row(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()
