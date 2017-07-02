from datetime import datetime
from tests.unittest.mock_class import TypeMatch


class TestTimeout:
    async def tearDown(self):
        await self.execute('''DROP TABLE timeout_logs''')
        await super().tearDown()

    async def test_record(self):
        await self.database.recordTimeout(
            'botgotsthis', 'botgotsthis', None, 'tests', None, None, None,
            None)
        self.assertEqual(
            await self.row('SELECT * FROM timeout_logs'),
            (1, TypeMatch(datetime), 'botgotsthis', 'botgotsthis', None,
             'tests', None, None, None, None))

    async def test_record2(self):
        await self.database.recordTimeout(
            'botgotsthis', 'megotsthis', 'mebotsthis', 'tests', 0, 3600,
            'Kappa', 'KappaHD')
        self.assertEqual(
            await self.row('SELECT * FROM timeout_logs'),
            (1, TypeMatch(datetime), 'botgotsthis', 'megotsthis', 'mebotsthis',
             'tests', 0, 3600, 'Kappa', 'KappaHD'))
