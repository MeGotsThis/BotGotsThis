from datetime import datetime
from tests.unittest.mock_class import TypeMatch
from ._drop_tables import TestDropTables


class TestBannedChannels(TestDropTables):
    async def test_list(self):
        self.assertEqual([b async for b in self.database.listBannedChannels()],
                         [])

    async def test_list_one(self):
        now = datetime(2000, 1, 1)
        await self.execute('INSERT INTO banned_channels VALUES (?, ?, ?, ?)',
                           ('botgotsthis', now, 'Kappa', 'botgotsthis'))
        self.assertEqual([b async for b in self.database.listBannedChannels()],
                         ['botgotsthis'])

    async def test_list_multiple(self):
        now = datetime(2000, 1, 1)
        await self.executemany(
            'INSERT INTO banned_channels VALUES (?, ?, ?, ?)',
            [('botgotsthis', now, 'Kappa', 'botgotsthis'),
             ('megotsthis', now, 'Kappa', 'botgotsthis'),
             ])
        self.assertEqual([b async for b in self.database.listBannedChannels()],
                         ['botgotsthis', 'megotsthis'])

    async def test_add(self):
        self.assertIs(
            await self.database.addBannedChannel(
                'botgotsthis', 'Kappa', 'megotsthis'),
            True)
        self.assertEqual(
            await self.row('SELECT * FROM banned_channels'),
            ('botgotsthis', TypeMatch(datetime), 'Kappa', 'megotsthis'))
        self.assertEqual(
            await self.row('SELECT * FROM banned_channels_log'),
            (1, 'botgotsthis', TypeMatch(datetime), 'Kappa', 'megotsthis',
             'add'))

    async def test_add_existing(self):
        now = datetime(2000, 1, 1)
        await self.execute('INSERT INTO banned_channels VALUES (?, ?, ?, ?)',
                           ('botgotsthis', now, 'Kappa', 'botgotsthis'))
        self.assertIs(
            await self.database.addBannedChannel(
                'botgotsthis', 'Kappa', 'megotsthis'),
            False)
        self.assertIsNone(await self.row('SELECT * FROM banned_channels_log'))

    async def test_remove(self):
        self.assertIs(
            await self.database.removeBannedChannel(
                'botgotsthis', 'Kappa', 'megotsthis'),
            False)

    async def test_remove_existing(self):
        now = datetime(2000, 1, 1)
        await self.execute('INSERT INTO banned_channels VALUES (?, ?, ?, ?)',
                           ('botgotsthis', now, 'Kappa', 'botgotsthis'))
        self.assertIs(
            await self.database.removeBannedChannel(
                'botgotsthis', 'Kappa', 'megotsthis'),
            True)
        self.assertIsNone(await self.row('SELECT * FROM banned_channels'))
        self.assertEqual(
            await self.row('SELECT * FROM banned_channels_log'),
            (1, 'botgotsthis', TypeMatch(datetime), 'Kappa', 'megotsthis',
             'remove'))
