import os
from tests.database.sqlite.test_database import TestSqlite


class TestSqliteGameAbbreviation(TestSqlite):
    def setUp(self):
        super().setUp()
        self.execute('''
CREATE TABLE chat_properties (
    broadcaster VARCHAR NOT NULL,
    property VARCHAR NOT NULL,
    value VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, property)
)''')

    def test_get_property(self):
        self.assertIsNone(
            self.database.getChatProperty('botgotsthis', 'kappa'))

    def test_get_property_default(self):
        self.assertEqual(
            self.database.getChatProperty('botgotsthis', 'kappa',
                                          default='Kappa'),
            'Kappa')

    def test_get_property_default_parse(self):
        self.assertEqual(
            self.database.getChatProperty('botgotsthis', 'kappa',
                                          default='Kappa', parse=int),
            'Kappa')

    def test_get_property_existing(self):
        self.execute('INSERT INTO chat_properties VALUES (?, ?, ?)',
                     ('botgotsthis', 'kappa', 'Kappa'))
        self.assertEqual(
            self.database.getChatProperty('botgotsthis', 'kappa'), 'Kappa')

    def test_get_property_existing_parse(self):
        self.execute('INSERT INTO chat_properties VALUES (?, ?, ?)',
                     ('botgotsthis', 'kappa', '0'))
        self.assertEqual(
            self.database.getChatProperty('botgotsthis', 'kappa', parse=int),
            0)

    def test_get_property_existing_default_parse(self):
        self.execute('INSERT INTO chat_properties VALUES (?, ?, ?)',
                     ('botgotsthis', 'kappa', '0'))
        self.assertEqual(
            self.database.getChatProperty('botgotsthis', 'kappa',
                                          default='Kappa', parse=int),
            0)

    def test_get_properties(self):
        self.assertEqual(
            self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd']),
            {'kappa': None, 'kappahd': None})

    def test_get_properties_one(self):
        self.execute('INSERT INTO chat_properties VALUES (?, ?, ?)',
                     ('botgotsthis', 'kappa', 'Kappa'))
        self.assertEqual(
            self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd']),
            {'kappa': 'Kappa', 'kappahd': None})

    def test_get_properties_two(self):
        self.executemany('INSERT INTO chat_properties VALUES (?, ?, ?)',
                         [('botgotsthis', 'kappa', 'Kappa'),
                          ('botgotsthis', 'kappahd', 'KappaHD')])
        self.assertEqual(
            self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd']),
            {'kappa': 'Kappa', 'kappahd': 'KappaHD'})

    def test_get_properties_default(self):
        self.assertEqual(
            self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'], default=0),
            {'kappa': 0, 'kappahd': 0})

    def test_get_properties_default_dict(self):
        self.assertEqual(
            self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'],
                default={'kappa': 'kappa', 'kappahd': 'kappahd'}),
            {'kappa': 'kappa', 'kappahd': 'kappahd'})

    def test_get_properties_default_partial(self):
        self.assertEqual(
            self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'], default={'kappa': None}),
            {'kappa': None})

    def test_get_properties_parse(self):
        self.assertEqual(
            self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'], parse=int),
            {'kappa': None, 'kappahd': None})

    def test_get_properties_parse_default(self):
        self.assertEqual(
            self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'], parse=int, default=''),
            {'kappa': '', 'kappahd': ''})

    def test_get_properties_parse_values(self):
        self.executemany('INSERT INTO chat_properties VALUES (?, ?, ?)',
                         [('botgotsthis', 'kappa', '1'),
                          ('botgotsthis', 'kappahd', '2')])
        self.assertEqual(
            self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'], parse=int),
            {'kappa': 1, 'kappahd': 2})

    def test_get_properties_parse_dict(self):
        self.executemany('INSERT INTO chat_properties VALUES (?, ?, ?)',
                         [('botgotsthis', 'kappa', '1'),
                          ('botgotsthis', 'kappahd', '2.5')])
        self.assertEqual(
            self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'],
                parse={'kappa': int, 'kappahd': float}),
            {'kappa': 1, 'kappahd': 2.5})

    def test_get_properties_parse_partial(self):
        self.executemany('INSERT INTO chat_properties VALUES (?, ?, ?)',
                         [('botgotsthis', 'kappa', '1'),
                          ('botgotsthis', 'kappahd', 'KappaHD')])
        self.assertEqual(
            self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'], parse={'kappa': int}),
            {'kappa': 1, 'kappahd': 'KappaHD'})

    def test_set_property(self):
        self.assertIs(self.database.setChatProperty('botgotsthis', 'kappa'),
                      False)
        self.assertIsNone(self.row('SELECT * FROM chat_properties'))

    def test_set_property_existing(self):
        self.execute('INSERT INTO chat_properties VALUES (?, ?, ?)',
                     ('botgotsthis', 'kappa', 'Kappa'))
        self.assertIs(self.database.setChatProperty('botgotsthis', 'kappa'),
                      True)
        self.assertIsNone(self.row('SELECT * FROM chat_properties'))

    def test_set_property_value(self):
        self.assertIs(
            self.database.setChatProperty('botgotsthis', 'kappa', 'Kappa'),
            True)
        self.assertEqual(self.row('SELECT * FROM chat_properties'),
                         ('botgotsthis', 'kappa', 'Kappa'))

    def test_set_property_value_existing(self):
        self.execute('INSERT INTO chat_properties VALUES (?, ?, ?)',
                     ('botgotsthis', 'kappa', 'Kappa'))
        self.assertIs(
            self.database.setChatProperty('botgotsthis', 'kappa', 'PogChamp'),
            True)
        self.assertEqual(self.row('SELECT * FROM chat_properties'),
                         ('botgotsthis', 'kappa', 'PogChamp'))
