from datetime import datetime
from tests.unittest.mock_class import TypeMatch


class TestBotManagers:
    async def tearDown(self):
        await self.execute(['''DROP TABLE bot_managers''',
                            '''DROP TABLE bot_managers_log'''])
        await super().tearDown()

    async def test_is_bot_manager_true(self):
        self.assertIs(await self.database.isBotManager('megotsthis'), True)

    async def test_is_bot_manager_false(self):
        self.assertIs(await self.database.isBotManager('mebotsthis'), False)

    async def test_add(self):
        self.assertIs(await self.database.addBotManager('mebotsthis'), True)
        self.assertEqual(
            await self.rows('SELECT * FROM bot_managers'),
            [('megotsthis',),
             ('mebotsthis',)])
        self.assertEqual(
            await self.row('SELECT * FROM bot_managers_log'),
            (1, 'mebotsthis', TypeMatch(datetime), 'add'))

    async def test_add_existing(self):
        self.assertIs(await self.database.addBotManager('megotsthis'), False)
        self.assertIsNone(await self.row('SELECT * FROM bot_managers_log'))

    async def test_remove(self):
        self.assertIs(await self.database.removeBotManager('mebotsthis'),
                      False)

    async def test_remove_existing(self):
        self.assertIs(await self.database.removeBotManager('megotsthis'), True)
        self.assertIsNone(await self.row('SELECT * FROM bot_managers'))
        self.assertEqual(
            await self.row('SELECT * FROM bot_managers_log'),
            (1, 'megotsthis', TypeMatch(datetime), 'remove'))
