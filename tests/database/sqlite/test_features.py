from tests.database.sqlite.test_database import TestSqlite


class TestSqliteFeatures(TestSqlite):
    async def setUp(self):
        await super().setUp()
        await self.execute('''
CREATE TABLE chat_features (
    broadcaster VARCHAR NOT NULL,
    feature VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, feature)
)''')

    async def tearDown(self):
        await self.execute('DROP TABLE IF EXISTS chat_features')
        await super().setUp()

    async def test_has(self):
        self.assertIs(await self.database.hasFeature('botgotsthis', 'feature'),
                      False)

    async def test_has_existing(self):
        await self.execute('INSERT INTO chat_features VALUES (?, ?)',
                           ('botgotsthis', 'feature'))
        self.assertIs(await self.database.hasFeature('botgotsthis', 'feature'),
                      True)

    async def test_add(self):
        self.assertIs(await self.database.addFeature('botgotsthis', 'feature'),
                      True)
        self.assertEqual(await self.row('SELECT * FROM chat_features'),
                         ('botgotsthis', 'feature'))

    async def test_add_existing(self):
        await self.execute('INSERT INTO chat_features VALUES (?, ?)',
                           ('botgotsthis', 'feature'))
        self.assertIs(await self.database.addFeature('botgotsthis', 'feature'),
                      False)

    async def test_remove(self):
        self.assertIs(
            await self.database.removeFeature('botgotsthis', 'feature'),
            False)

    async def test_remove_existing(self):
        await self.execute('INSERT INTO chat_features VALUES (?, ?)',
                           ('botgotsthis', 'feature'))
        self.assertIs(
            await self.database.removeFeature('botgotsthis', 'feature'),
            True)
        self.assertIsNone(await self.row('SELECT * FROM chat_features'))
