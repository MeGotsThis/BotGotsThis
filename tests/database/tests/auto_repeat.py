from datetime import datetime, timedelta
from lib.database import AutoRepeatList, AutoRepeatMessage
from tests.unittest.mock_class import DateTimeNear
from ._drop_tables import TestDropTables


class TestAutoRepeat(TestDropTables):
    async def test_empty(self):
        self.assertEqual(
            [r async for r in self.database.getAutoRepeatToSend()], [])

    async def test_nothing_to_send(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        await self.execute(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            ('botgotsthis', '', 'Kappa', None, 5, dt, dt))
        self.assertEqual(
            [r async for r in self.database.getAutoRepeatToSend()], [])

    async def test_something_to_send(self):
        await self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 5,
              datetime.utcnow() - timedelta(minutes=5), datetime.utcnow()),
             ('botgotsthis', 'kappa', 'Kappa', None, 5,
              datetime.utcnow(), datetime.utcnow())
             ])
        self.assertEqual(
            [r async for r in self.database.getAutoRepeatToSend()],
            [AutoRepeatMessage('botgotsthis', '', 'Kappa')])

    async def test_something_to_send_decimal(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        await self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 0.1,
              dt - timedelta(seconds=6), dt),
             ('botgotsthis', 'kappa', 'Kappa', None, 5,
              dt - timedelta(seconds=5), dt)
             ])
        self.assertEqual(
            [r async for r in self.database.getAutoRepeatToSend()],
            [AutoRepeatMessage('botgotsthis', '', 'Kappa')])

    async def test_something_to_send_count(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        await self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', 10, 5,
              dt - timedelta(minutes=5), dt),
             ('botgotsthis', 'kappa', 'Kappa', 10, 5,
              dt, dt)
             ])
        self.assertEqual(
            [r async for r in self.database.getAutoRepeatToSend()],
            [AutoRepeatMessage('botgotsthis', '', 'Kappa')])

    async def test_something_to_send_multiple(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        await self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', 10, 5,
              dt - timedelta(minutes=5), dt),
             ('botgotsthis', 'kappa', 'Kappa', None, 5,
              dt - timedelta(minutes=5), dt)
             ])
        self.assertEqual(
            [r async for r in self.database.getAutoRepeatToSend()],
            [AutoRepeatMessage('botgotsthis', '', 'Kappa'),
             AutoRepeatMessage('botgotsthis', 'kappa', 'Kappa')])

    async def test_list_empty(self):
        self.assertEqual(
            [r async for r in self.database.listAutoRepeat('botgotsthis')],
            [])

    async def test_list(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        await self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 0.1, dt, dt),
             ('botgotsthis', 'kappa', 'Kappa', 10, 5, dt, dt)
             ])
        self.assertEqual(
            [r async for r in self.database.listAutoRepeat('botgotsthis')],
            [AutoRepeatList('', 'Kappa', None, 0.1, dt),
             AutoRepeatList('kappa', 'Kappa', 10, 5, dt)])

    async def test_clear_empty(self):
        self.assertFalse(await self.database.clearAutoRepeat('botgotsthis'))
        self.assertEqual(await self.rows('SELECT * FROM auto_repeat'), [])
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        await self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 0.1, dt, dt),
             ('botgotsthis', 'kappa', 'Kappa', 10, 5, dt, dt)
             ])
        self.assertFalse(await self.database.clearAutoRepeat('megotsthis'))
        self.assertEqual(
            await self.rows('SELECT * FROM auto_repeat'),
            [('botgotsthis', '', 'Kappa', None, 0.1, dt, dt),
             ('botgotsthis', 'kappa', 'Kappa', 10, 5, dt, dt),
             ])

    async def test_clear(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        await self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 0.1, dt, dt),
             ('botgotsthis', 'kappa', 'Kappa', 10, 5, dt, dt)
             ])
        self.assertTrue(await self.database.clearAutoRepeat('botgotsthis'))
        self.assertEqual(await self.rows('SELECT * FROM auto_repeat'), [])

    async def test_message_sent(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        await self.executemany(
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
        self.assertTrue(
            await self.database.sentAutoRepeat('botgotsthis', ''))
        self.assertTrue(
            await self.database.sentAutoRepeat('botgotsthis', 'kappa'))
        self.assertTrue(
            await self.database.sentAutoRepeat('botgotsthis', ':)'))
        self.assertTrue(
            await self.database.sentAutoRepeat('botgotsthis', ':('))
        self.maxDiff = None

        self.assertEqual(
            await self.rows(
                 'SELECT * FROM auto_repeat ORDER BY broadcaster, name'),
            [('botgotsthis', '', 'Kappa', None, 0.1, DateTimeNear(dt),
              DateTimeNear(dt)),
             ('botgotsthis', 'kappa', 'Kappa', 9, 5, DateTimeNear(dt),
              DateTimeNear(dt)),
             ('botgotsthis', 'keepo', 'Keepo', None, 5, DateTimeNear(dt),
              DateTimeNear(dt)),
             ('botgotsthis', 'vohiyo', 'VoHiYo', 10, 5, DateTimeNear(dt),
              DateTimeNear(dt)),
             ])

    async def test_set_auto_repeat(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.assertTrue(
            await self.database.setAutoRepeat(
                'botgotsthis', '', 'Kappa', None, 5))
        self.assertEqual(
            await self.rows('SELECT * FROM auto_repeat'),
            [('botgotsthis', '', 'Kappa', None, 5,
              DateTimeNear(dt - timedelta(minutes=5)), DateTimeNear(dt)),
             ])

    async def test_set_auto_repeat_multiple(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.assertTrue(
            await self.database.setAutoRepeat(
                'botgotsthis', '', 'Kappa', None, 5))
        self.assertTrue(
            await self.database.setAutoRepeat(
                'botgotsthis', '', 'Keepo', None, 5))
        self.assertEqual(
            await self.rows('SELECT * FROM auto_repeat'),
            [('botgotsthis', '', 'Keepo', None, 5,
              DateTimeNear(dt - timedelta(minutes=5)), DateTimeNear(dt)),
             ])

    async def test_set_auto_repeat_multiple_names(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.assertTrue(
            await self.database.setAutoRepeat(
                'botgotsthis', '', 'Kappa', None, 5))
        self.assertTrue(
            await self.database.setAutoRepeat(
                'botgotsthis', 'Kappa', 'Keepo', None, 5))
        self.assertEqual(
            await self.rows('SELECT * FROM auto_repeat'),
            [('botgotsthis', '', 'Kappa', None, 5,
              DateTimeNear(dt - timedelta(minutes=5)), DateTimeNear(dt)),
             ('botgotsthis', 'Kappa', 'Keepo', None, 5,
              DateTimeNear(dt - timedelta(minutes=5)), DateTimeNear(dt)),
             ])

    async def test_delete(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        await self.executemany(
            "INSERT INTO auto_repeat VALUES (?, ?, ?, ?, ?, ?, ?)",
            [('botgotsthis', '', 'Kappa', None, 5, dt, dt),
             ('botgotsthis', 'kappa', 'Kappa', None, 5, dt, dt)
             ])
        self.assertTrue(
            await self.database.removeAutoRepeat('botgotsthis', ''))
        self.assertEqual(
            await self.rows('SELECT * FROM auto_repeat'),
            [('botgotsthis', 'kappa', 'Kappa', None, 5, dt, dt),
             ])

    async def test_delete_not_existing(self):
        dt = datetime.utcnow()
        dt -= timedelta(microseconds=dt.microsecond)
        self.assertFalse(
            await self.database.removeAutoRepeat('botgotsthis', ''))
        self.assertEqual(await self.rows('SELECT * FROM auto_repeat'), [])
