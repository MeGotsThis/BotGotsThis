import bot  # noqa: F401

from tests.unittest.mock_class import AsyncIterator
from .base_cache_store import TestCacheStore


class TestCacheCustomCommands(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        self.dbmain.getCustomCommands.side_effect = lambda *_: AsyncIterator([
            ('kappa', '', 'Kappa'),
            ('kappa', 'owner', 'Kappa'),
        ])
        getCustomCommandProperties = self.dbmain.getCustomCommandProperties
        getCustomCommandProperties.side_effect = lambda *_: AsyncIterator([
            ('kappa', '', 'prop', 'value'),
        ])

        self.channel = 'megotsthis'
        self.key = f'twitch:{self.channel}:commands'

    async def test_load(self):
        self.assertEqual(
            await self.data.loadCustomCommands(self.channel),
            {
                'kappa': {
                    '': ('Kappa', {'prop': 'value'}),
                    'owner': ('Kappa', {}),
                }
            })
        self.assertTrue(self.dbmain.getCustomCommands.called)
        self.assertTrue(self.dbmain.getCustomCommandProperties.called)
        self.assertIsNotNone(await self.redis.get(self.key))

    async def test_get_chat_commands(self):
        self.assertEqual(
            await self.data.getChatCommands(self.channel, 'kappa'),
            {
                self.channel: {
                    '': 'Kappa',
                    'owner': 'Kappa',
                },
                '#global': {
                    '': 'Kappa',
                    'owner': 'Kappa',
                },
            })
        self.assertTrue(self.dbmain.getCustomCommands.called)
        self.assertTrue(self.dbmain.getCustomCommandProperties.called)
        self.dbmain.getCustomCommands.reset_mock()
        self.dbmain.getCustomCommandProperties.reset_mock()
        self.assertEqual(
            await self.data.getChatCommands(self.channel, ''),
            {
                self.channel: {},
                '#global': {},
            })
        self.assertFalse(self.dbmain.getCustomCommands.called)
        self.assertFalse(self.dbmain.getCustomCommandProperties.called)
        self.assertIsNotNone(await self.redis.get(self.key))

    async def test_get_custom_command(self):
        self.assertEqual(
            await self.data.getCustomCommand(self.channel, '', 'kappa'),
            'Kappa')
        self.assertTrue(self.dbmain.getCustomCommands.called)
        self.assertTrue(self.dbmain.getCustomCommandProperties.called)
        self.dbmain.getCustomCommands.reset_mock()
        self.dbmain.getCustomCommandProperties.reset_mock()
        self.assertIsNone(
            await self.data.getCustomCommand(self.channel, 'moderator',
                                             'kappa'))
        self.assertIsNone(
            await self.data.getCustomCommand(self.channel, '', 'kappahd'))
        self.assertFalse(self.dbmain.getCustomCommands.called)
        self.assertFalse(self.dbmain.getCustomCommandProperties.called)
        self.assertIsNotNone(await self.redis.get(self.key))

    async def test_get_custom_command_property(self):
        self.assertEqual(
            await self.data.getCustomCommandProperty(
                self.channel, '', 'kappa', 'prop'),
            'value')
        self.assertTrue(self.dbmain.getCustomCommands.called)
        self.assertTrue(self.dbmain.getCustomCommandProperties.called)
        self.dbmain.getCustomCommands.reset_mock()
        self.dbmain.getCustomCommandProperties.reset_mock()
        self.assertIsNone(
            await self.data.getCustomCommandProperty(
                self.channel, '', 'kappa', 'key'))
        self.assertIsNone(
            await self.data.getCustomCommandProperty(
                self.channel, '', 'kappahd', 'prop'))
        self.assertIsNone(
            await self.data.getCustomCommandProperty(
                self.channel, 'moderator', 'kappa', 'prop'))
        self.assertFalse(self.dbmain.getCustomCommands.called)
        self.assertFalse(self.dbmain.getCustomCommandProperties.called)
        self.assertIsNotNone(await self.redis.get(self.key))

    async def test_reset(self):
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        await self.data.resetCustomCommands(self.channel)
        self.assertIsNone(await self.redis.get(self.key))

    async def test_insert(self):
        self.dbmain.insertCustomCommand.return_value = True
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.insertCustomCommand(
                self.channel, '', 'kappa', 'Kappa', 'botgotsthis'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.insertCustomCommand.called)

    async def test_insert_false(self):
        self.dbmain.insertCustomCommand.return_value = False
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.insertCustomCommand(
                self.channel, '', 'kappa', 'Kappa', 'botgotsthis'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.insertCustomCommand.called)

    async def test_update(self):
        self.dbmain.updateCustomCommand.return_value = True
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.updateCustomCommand(
                self.channel, '', 'kappa', 'Kappa', 'botgotsthis'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.updateCustomCommand.called)

    async def test_update_false(self):
        self.dbmain.updateCustomCommand.return_value = False
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.updateCustomCommand(
                self.channel, '', 'kappa', 'Kappa', 'botgotsthis'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.updateCustomCommand.called)

    async def test_append(self):
        self.dbmain.appendCustomCommand.return_value = True
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.appendCustomCommand(
                self.channel, '', 'kappa', 'Kappa', 'botgotsthis'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.appendCustomCommand.called)

    async def test_append_false(self):
        self.dbmain.appendCustomCommand.return_value = False
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.appendCustomCommand(
                self.channel, '', 'kappa', 'Kappa', 'botgotsthis'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.appendCustomCommand.called)

    async def test_replace(self):
        self.dbmain.replaceCustomCommand.return_value = True
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.replaceCustomCommand(
                self.channel, '', 'kappa', 'Kappa', 'botgotsthis'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.replaceCustomCommand.called)

    async def test_replace_false(self):
        self.dbmain.replaceCustomCommand.return_value = False
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.replaceCustomCommand(
                self.channel, '', 'kappa', 'Kappa', 'botgotsthis'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.replaceCustomCommand.called)

    async def test_delete(self):
        self.dbmain.deleteCustomCommand.return_value = True
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.deleteCustomCommand(
                self.channel, '', 'kappa', 'botgotsthis'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.deleteCustomCommand.called)

    async def test_delete_false(self):
        self.dbmain.deleteCustomCommand.return_value = False
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.deleteCustomCommand(
                self.channel, '', 'kappa', 'botgotsthis'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.deleteCustomCommand.called)

    async def test_level(self):
        self.dbmain.levelCustomCommand.return_value = True
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.levelCustomCommand(
                self.channel, '', 'kappa', 'botgotsthis', 'owner'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.levelCustomCommand.called)

    async def test_level_false(self):
        self.dbmain.levelCustomCommand.return_value = False
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.levelCustomCommand(
                self.channel, '', 'kappa', 'botgotsthis', 'owner'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.levelCustomCommand.called)

    async def test_rename(self):
        self.dbmain.renameCustomCommand.return_value = True
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.renameCustomCommand(
                self.channel, '', 'kappa', 'botgotsthis', 'kappahd'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.renameCustomCommand.called)

    async def test_rename_false(self):
        self.dbmain.renameCustomCommand.return_value = False
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.renameCustomCommand(
                self.channel, '', 'kappa', 'botgotsthis', 'kappahd'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.renameCustomCommand.called)

    async def test_property(self):
        self.dbmain.processCustomCommandProperty.return_value = True
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.processCustomCommandProperty(
                self.channel, '', 'kappa', 'prop'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.processCustomCommandProperty.called)

    async def test_property_false(self):
        self.dbmain.processCustomCommandProperty.return_value = False
        await self.data.loadCustomCommands(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.processCustomCommandProperty(
                self.channel, '', 'kappa', 'prop'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.processCustomCommandProperty.called)
