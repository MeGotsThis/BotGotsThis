from datetime import datetime, timedelta

import bot  # noqa: F401

from lib.data import AutoRepeatMessage, AutoRepeatList, RepeatData
from tests.unittest.mock_class import AsyncIterator
from .base_cache_store import TestCacheStore


class TestCacheAutoRepeat(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        self.now = datetime.utcnow()

        self.dbmain.getAutoRepeats.return_value = AsyncIterator([
            RepeatData('botgotsthis', '', 'FrankerZ', None, 1, self.now),
            RepeatData('megotsthis', '', 'Kappa', None, 1,
                       self.now - timedelta(minutes=1)),
        ])

    async def test_load(self):
        self.assertEqual(
            await self.data.loadAutoRepeats(),
            [RepeatData('botgotsthis', '', 'FrankerZ', None, 1, self.now),
             RepeatData('megotsthis', '', 'Kappa', None, 1,
                        self.now - timedelta(minutes=1)),
             ])
        self.assertTrue(self.dbmain.getAutoRepeats.called)
        self.assertIsNotNone(await self.redis.get('autorepeat'))

    async def test(self):
        self.assertEqual(
            [r async for r in self.data.getAutoRepeatToSend(self.now)],
            [AutoRepeatMessage('megotsthis', '', 'Kappa')])
        self.assertTrue(self.dbmain.getAutoRepeats.called)
        self.dbmain.getAutoRepeats.reset_mock()
        self.assertEqual(
            [r async for r in self.data.getAutoRepeatToSend(self.now)],
            [AutoRepeatMessage('megotsthis', '', 'Kappa')])
        self.assertFalse(self.dbmain.getAutoRepeats.called)
        self.assertEqual(
            [r async for r in self.data.listAutoRepeat('botgotsthis')],
            [AutoRepeatList('', 'FrankerZ', None, 1, self.now)])
        self.assertFalse(self.dbmain.getAutoRepeats.called)
        self.assertIsNotNone(await self.redis.get('autorepeat'))

    async def test_empty(self):
        self.dbmain.getAutoRepeats.return_value = AsyncIterator([])
        self.assertEqual(
            [r async for r in self.data.getAutoRepeatToSend(self.now)], [])

    async def test_nothing_to_send(self):
        self.dbmain.getAutoRepeats.return_value = AsyncIterator([
            RepeatData('botgotsthis', '', 'FrankerZ', None, 1, self.now),
        ])
        self.assertEqual(
            [r async for r in self.data.getAutoRepeatToSend(self.now)], [])

    async def test_something_to_send(self):
        self.assertEqual(
            [r async for r in self.data.getAutoRepeatToSend(self.now)],
            [AutoRepeatMessage('megotsthis', '', 'Kappa')])

    async def test_something_to_send_decimal(self):
        self.dbmain.getAutoRepeats.return_value = AsyncIterator([
            RepeatData('botgotsthis', '', 'FrankerZ', None, 1,
                       self.now - timedelta(seconds=5)),
            RepeatData('megotsthis', '', 'Kappa', None, 0.1,
                       self.now - timedelta(seconds=6)),
        ])
        self.assertEqual(
            [r async for r in self.data.getAutoRepeatToSend()],
            [AutoRepeatMessage('megotsthis', '', 'Kappa')])

    async def test_something_to_send_count(self):
        self.dbmain.getAutoRepeats.return_value = AsyncIterator([
            RepeatData('botgotsthis', '', 'FrankerZ', 10, 1, self.now),
            RepeatData('megotsthis', '', 'Kappa', 10, 1,
                       self.now - timedelta(minutes=1)),
        ])
        self.assertEqual(
            [r async for r in self.data.getAutoRepeatToSend()],
            [AutoRepeatMessage('megotsthis', '', 'Kappa')])

    async def test_something_to_send_multiple(self):
        self.dbmain.getAutoRepeats.return_value = AsyncIterator([
            RepeatData('botgotsthis', '', 'FrankerZ', 10, 1,
                       self.now - timedelta(minutes=1)),
            RepeatData('megotsthis', '', 'Kappa', 10, 1,
                       self.now - timedelta(minutes=1)),
        ])
        self.assertEqual(
            [r async for r in self.data.getAutoRepeatToSend()],
            [AutoRepeatMessage('botgotsthis', '', 'FrankerZ'),
             AutoRepeatMessage('megotsthis', '', 'Kappa')])

    async def test_list_empty(self):
        self.dbmain.getAutoRepeats.return_value = AsyncIterator([])
        self.assertEqual(
            [r async for r in self.data.listAutoRepeat('botgotsthis')],
            [])

    async def test_list(self):
        self.assertEqual(
            [r async for r in self.data.listAutoRepeat('botgotsthis')],
            [AutoRepeatList('', 'FrankerZ', None, 1, self.now)])

    async def test_reset(self):
        await self.data.loadBotManagers()
        self.assertIsNotNone(await self.redis.get('managers'))
        await self.data.resetBotManagers()
        self.assertIsNone(await self.redis.get('managers'))

    async def test_add(self):
        self.dbmain.addBotManager.return_value = True
        await self.data.loadBotManagers()
        self.assertIsNotNone(await self.redis.get('managers'))
        self.assertIs(await self.data.addBotManager('megotsthis'), True)
        self.assertIsNone(await self.redis.get('managers'))
        self.assertTrue(self.dbmain.addBotManager.called)

    async def test_add_false(self):
        self.dbmain.addBotManager.return_value = False
        await self.data.loadBotManagers()
        self.assertIsNotNone(await self.redis.get('managers'))
        self.assertIs(await self.data.addBotManager('megotsthis'), False)
        self.assertIsNotNone(await self.redis.get('managers'))
        self.assertTrue(self.dbmain.addBotManager.called)

    async def test_remove(self):
        self.dbmain.removeBotManager.return_value = True
        await self.data.loadBotManagers()
        self.assertIsNotNone(await self.redis.get('managers'))
        self.assertIs(await self.data.removeBotManager('megotsthis'), True)
        self.assertIsNone(await self.redis.get('managers'))
        self.assertTrue(self.dbmain.removeBotManager.called)

    async def test_remove_false(self):
        self.dbmain.removeBotManager.return_value = False
        await self.data.loadBotManagers()
        self.assertIsNotNone(await self.redis.get('managers'))
        self.assertIs(await self.data.removeBotManager('megotsthis'), False)
        self.assertIsNotNone(await self.redis.get('managers'))
        self.assertTrue(self.dbmain.removeBotManager.called)
