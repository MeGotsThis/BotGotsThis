import math
from lib.data import AutoJoinChannel
from ._drop_tables import TestDropTables


class TestAutoJoin(TestDropTables):
    async def test_chats_empty(self):
        self.assertEqual([c async for c in self.database.getAutoJoinsChats()],
                         [])

    async def test_chat(self):
        await self.execute("INSERT INTO auto_join VALUES (?, ?, ?)",
                           ('botgotsthis', 0, 'main'))
        self.assertEqual([c async for c in self.database.getAutoJoinsChats()],
                         [AutoJoinChannel('botgotsthis', 0, 'main')])

    async def test_chats(self):
        await self.executemany("INSERT INTO auto_join VALUES (?, ?, ?)",
                               [('botgotsthis', 0, 'main'),
                                ('megotsthis', -1, 'twitch'),
                                ('mebotsthis', 1, 'aws')])
        self.assertEqual([c async for c in self.database.getAutoJoinsChats()],
                         [AutoJoinChannel('megotsthis', -1, 'twitch'),
                          AutoJoinChannel('botgotsthis', 0, 'main'),
                          AutoJoinChannel('mebotsthis', 1, 'aws')])

    async def test_priority_not_existing(self):
        self.assertEqual(
            await self.database.getAutoJoinsPriority('botgotsthis'),
            math.inf)

    async def test_priority(self):
        await self.execute("INSERT INTO auto_join VALUES (?, ?, ?)",
                           ('botgotsthis', 0, 'main'))
        self.assertEqual(
            await self.database.getAutoJoinsPriority('botgotsthis'), 0)

    async def test_save(self):
        self.assertIs(
            await self.database.saveAutoJoin('botgotsthis', 0, 'twitch'),
            True)
        self.assertEqual(await self.row('SELECT * FROM auto_join'),
                         ('botgotsthis', 0, 'twitch'))

    async def test_save_existing(self):
        await self.execute("INSERT INTO auto_join VALUES (?, ?, ?)",
                           ('botgotsthis', -1, 'main'))
        self.assertIs(
            await self.database.saveAutoJoin('botgotsthis', 0, 'twitch'),
            False)
        self.assertEqual(await self.row('SELECT * FROM auto_join'),
                         ('botgotsthis', -1, 'main'))

    async def test_discard(self):
        await self.execute("INSERT INTO auto_join VALUES (?, ?, ?)",
                           ('botgotsthis', 0, 'main'))
        self.assertIs(await self.database.discardAutoJoin('botgotsthis'), True)
        self.assertIsNone(await self.row('SELECT * FROM auto_join'))

    async def test_discard_not_existing(self):
        self.assertIs(await self.database.discardAutoJoin('botgotsthis'),
                      False)
        self.assertIsNone(await self.row('SELECT * FROM auto_join'))

    async def test_save_priority(self):
        await self.execute("INSERT INTO auto_join VALUES (?, ?, ?)",
                           ('botgotsthis', 0, 'main'))
        self.assertIs(
            await self.database.setAutoJoinPriority('botgotsthis', -1),
            True)
        self.assertEqual(await self.row('SELECT * FROM auto_join'),
                         ('botgotsthis', -1, 'main'))

    async def test_save_priority_not_existing(self):
        self.assertIs(
            await self.database.setAutoJoinPriority('botgotsthis', 0),
            False)
        self.assertIsNone(await self.row('SELECT * FROM auto_join'))

    async def test_save_server(self):
        await self.execute("INSERT INTO auto_join VALUES (?, ?, ?)",
                           ('botgotsthis', 0, 'main'))
        self.assertIs(
            await self.database.setAutoJoinServer('botgotsthis', 'twitch'),
            True)
        self.assertEqual(await self.row('SELECT * FROM auto_join'),
                         ('botgotsthis', 0, 'twitch'))

    async def test_save_server_not_existing(self):
        self.assertIs(
            await self.database.setAutoJoinServer('botgotsthis', 'twitch'),
            False)
        self.assertIsNone(await self.row('SELECT * FROM auto_join'))
