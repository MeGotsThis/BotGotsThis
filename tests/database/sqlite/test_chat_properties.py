from tests.database.sqlite.test_database import TestSqlite


class TestSqliteGameAbbreviation(TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.execute('''
CREATE TABLE chat_properties (
    broadcaster VARCHAR NOT NULL,
    property VARCHAR NOT NULL,
    value VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, property)
)''')

    async def test_get_property(self):
        self.assertIsNone(
            await self.database.getChatProperty('botgotsthis', 'kappa'))

    async def test_get_property_default(self):
        self.assertEqual(
            await self.database.getChatProperty('botgotsthis', 'kappa',
                                                default='Kappa'),
            'Kappa')

    async def test_get_property_default_parse(self):
        self.assertEqual(
            await self.database.getChatProperty('botgotsthis', 'kappa',
                                                default='Kappa', parse=int),
            'Kappa')

    async def test_get_property_existing(self):
        await self.execute('INSERT INTO chat_properties VALUES (?, ?, ?)',
                           ('botgotsthis', 'kappa', 'Kappa'))
        self.assertEqual(
            await self.database.getChatProperty('botgotsthis', 'kappa'),
            'Kappa')

    async def test_get_property_existing_parse(self):
        await self.execute('INSERT INTO chat_properties VALUES (?, ?, ?)',
                           ('botgotsthis', 'kappa', '0'))
        self.assertEqual(
            await self.database.getChatProperty('botgotsthis', 'kappa',
                                                parse=int),
            0)

    async def test_get_property_existing_default_parse(self):
        await self.execute('INSERT INTO chat_properties VALUES (?, ?, ?)',
                           ('botgotsthis', 'kappa', '0'))
        self.assertEqual(
            await self.database.getChatProperty('botgotsthis', 'kappa',
                                                default='Kappa', parse=int),
            0)

    async def test_get_properties(self):
        self.assertEqual(
            await self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd']),
            {'kappa': None, 'kappahd': None})

    async def test_get_properties_one(self):
        await self.execute('INSERT INTO chat_properties VALUES (?, ?, ?)',
                     ('botgotsthis', 'kappa', 'Kappa'))
        self.assertEqual(
            await self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd']),
            {'kappa': 'Kappa', 'kappahd': None})

    async def test_get_properties_two(self):
        await self.executemany('INSERT INTO chat_properties VALUES (?, ?, ?)',
                               [('botgotsthis', 'kappa', 'Kappa'),
                                ('botgotsthis', 'kappahd', 'KappaHD')])
        self.assertEqual(
            await self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd']),
            {'kappa': 'Kappa', 'kappahd': 'KappaHD'})

    async def test_get_properties_default(self):
        self.assertEqual(
            await self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'], default=0),
            {'kappa': 0, 'kappahd': 0})

    async def test_get_properties_default_dict(self):
        self.assertEqual(
            await self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'],
                default={'kappa': 'kappa', 'kappahd': 'kappahd'}),
            {'kappa': 'kappa', 'kappahd': 'kappahd'})

    async def test_get_properties_default_partial(self):
        self.assertEqual(
            await self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'], default={'kappa': None}),
            {'kappa': None})

    async def test_get_properties_parse(self):
        self.assertEqual(
            await self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'], parse=int),
            {'kappa': None, 'kappahd': None})

    async def test_get_properties_parse_default(self):
        self.assertEqual(
            await self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'], parse=int, default=''),
            {'kappa': '', 'kappahd': ''})

    async def test_get_properties_parse_values(self):
        await self.executemany('INSERT INTO chat_properties VALUES (?, ?, ?)',
                               [('botgotsthis', 'kappa', '1'),
                                ('botgotsthis', 'kappahd', '2')])
        self.assertEqual(
            await self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'], parse=int),
            {'kappa': 1, 'kappahd': 2})

    async def test_get_properties_parse_dict(self):
        await self.executemany('INSERT INTO chat_properties VALUES (?, ?, ?)',
                               [('botgotsthis', 'kappa', '1'),
                                ('botgotsthis', 'kappahd', '2.5')])
        self.assertEqual(
            await self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'],
                parse={'kappa': int, 'kappahd': float}),
            {'kappa': 1, 'kappahd': 2.5})

    async def test_get_properties_parse_partial(self):
        await self.executemany('INSERT INTO chat_properties VALUES (?, ?, ?)',
                               [('botgotsthis', 'kappa', '1'),
                                ('botgotsthis', 'kappahd', 'KappaHD')])
        self.assertEqual(
            await self.database.getChatProperties(
                'botgotsthis', ['kappa', 'kappahd'], parse={'kappa': int}),
            {'kappa': 1, 'kappahd': 'KappaHD'})

    async def test_set_property(self):
        self.assertIs(
            await self.database.setChatProperty('botgotsthis', 'kappa'),
            False)
        self.assertIsNone(await self.row('SELECT * FROM chat_properties'))

    async def test_set_property_existing(self):
        await self.execute('INSERT INTO chat_properties VALUES (?, ?, ?)',
                     ('botgotsthis', 'kappa', 'Kappa'))
        self.assertIs(await self.database.setChatProperty('botgotsthis',
                                                          'kappa'),
                      True)
        self.assertIsNone(await self.row('SELECT * FROM chat_properties'))

    async def test_set_property_value(self):
        self.assertIs(
            await self.database.setChatProperty('botgotsthis', 'kappa',
                                                'Kappa'),
            True)
        self.assertEqual(await self.row('SELECT * FROM chat_properties'),
                         ('botgotsthis', 'kappa', 'Kappa'))

    async def test_set_property_value_existing(self):
        await self.execute('INSERT INTO chat_properties VALUES (?, ?, ?)',
                           ('botgotsthis', 'kappa', 'Kappa'))
        self.assertIs(
            await self.database.setChatProperty('botgotsthis', 'kappa',
                                                'PogChamp'),
            True)
        self.assertEqual(await self.row('SELECT * FROM chat_properties'),
                         ('botgotsthis', 'kappa', 'PogChamp'))
