import math
from lib.data import AutoJoinChannel
from ._drop_tables import TestDropTables


class TestAutoJoin(TestDropTables):
    async def test_chats_empty(self):
        self.assertEqual([c async for c in self.database.getAutoJoinsChats()],
                         [])

    async def test_chat(self):
        await self.execute("INSERT INTO auto_join VALUES (?, ?)",
                           ('botgotsthis', 0))
        self.assertEqual([c async for c in self.database.getAutoJoinsChats()],
                         [AutoJoinChannel('botgotsthis', 0)])

    async def test_chats(self):
        await self.executemany("INSERT INTO auto_join VALUES (?, ?)",
                               [('botgotsthis', 0),
                                ('megotsthis', -1),
                                ('mebotsthis', 1)])
        self.assertEqual([c async for c in self.database.getAutoJoinsChats()],
                         [AutoJoinChannel('megotsthis', -1),
                          AutoJoinChannel('botgotsthis', 0),
                          AutoJoinChannel('mebotsthis', 1)])

    async def test_priority_not_existing(self):
        self.assertEqual(
            await self.database.getAutoJoinsPriority('botgotsthis'),
            math.inf)

    async def test_priority(self):
        await self.execute("INSERT INTO auto_join VALUES (?, ?)",
                           ('botgotsthis', 0))
        self.assertEqual(
            await self.database.getAutoJoinsPriority('botgotsthis'), 0)

    async def test_save(self):
        self.assertIs(
            await self.database.saveAutoJoin('botgotsthis', 0),
            True)
        self.assertEqual(await self.row('SELECT * FROM auto_join'),
                         ('botgotsthis', 0))

    async def test_save_existing(self):
        await self.execute("INSERT INTO auto_join VALUES (?, ?)",
                           ('botgotsthis', -1))
        self.assertIs(
            await self.database.saveAutoJoin('botgotsthis', 0),
            False)
        self.assertEqual(await self.row('SELECT * FROM auto_join'),
                         ('botgotsthis', -1))

    async def test_discard(self):
        await self.execute("INSERT INTO auto_join VALUES (?, ?)",
                           ('botgotsthis', 0))
        self.assertIs(await self.database.discardAutoJoin('botgotsthis'), True)
        self.assertIsNone(await self.row('SELECT * FROM auto_join'))

    async def test_discard_not_existing(self):
        self.assertIs(await self.database.discardAutoJoin('botgotsthis'),
                      False)
        self.assertIsNone(await self.row('SELECT * FROM auto_join'))

    async def test_save_priority(self):
        await self.execute("INSERT INTO auto_join VALUES (?, ?)",
                           ('botgotsthis', 0))
        self.assertIs(
            await self.database.setAutoJoinPriority('botgotsthis', -1),
            True)
        self.assertEqual(await self.row('SELECT * FROM auto_join'),
                         ('botgotsthis', -1))

    async def test_save_priority_not_existing(self):
        self.assertIs(
            await self.database.setAutoJoinPriority('botgotsthis', 0),
            False)
        self.assertIsNone(await self.row('SELECT * FROM auto_join'))
