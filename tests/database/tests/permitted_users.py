from datetime import datetime
from tests.unittest.mock_class import TypeMatch
from ._drop_tables import TestDropTables


class TestPermittedUsers(TestDropTables):
    async def setUpInsert(self):
        await self.execute(['''
INSERT INTO permitted_users VALUES ('botgotsthis', 'megotsthis')'''])

    async def test_is_permitted_true(self):
        self.assertIs(
            await self.database.isPermittedUser('botgotsthis', 'megotsthis'),
            True)

    async def test_is_permitted_false(self):
        self.assertIs(
            await self.database.isPermittedUser('botgotsthis', 'mebotsthis'),
            False)

    async def test_add(self):
        self.assertIs(
            await self.database.addPermittedUser(
                'botgotsthis', 'mebotsthis', 'megotsthis'),
            True)
        self.assertEqual(
            await self.rows('SELECT * FROM permitted_users'),
            [('botgotsthis', 'megotsthis'),
             ('botgotsthis', 'mebotsthis')])
        self.assertEqual(
            await self.row('SELECT * FROM permitted_users_log'),
            (1, 'botgotsthis', 'mebotsthis', 'megotsthis', TypeMatch(datetime),
             'add'))

    async def test_add_existing(self):
        self.assertIs(
            await self.database.addPermittedUser(
                'botgotsthis', 'megotsthis', 'megotsthis'),
            False)
        self.assertIsNone(await self.row('SELECT * FROM permitted_users_log'))

    async def test_remove(self):
        self.assertIs(
            await self.database.removePermittedUser(
                'botgotsthis', 'mebotsthis', 'megotsthis'),
            False)

    async def test_remove_existing(self):
        self.assertIs(
            await self.database.removePermittedUser(
                'botgotsthis', 'megotsthis', 'megotsthis'),
            True)
        self.assertIsNone(await self.row('SELECT * FROM permitted_users'))
        self.assertEqual(
            await self.row('SELECT * FROM permitted_users_log'),
            (1, 'botgotsthis', 'megotsthis', 'megotsthis', TypeMatch(datetime),
             'remove'))
