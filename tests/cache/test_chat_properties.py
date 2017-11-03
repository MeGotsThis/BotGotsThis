import bot  # noqa: F401

from tests.unittest.mock_class import AsyncIterator
from .base_cache_store import TestCacheStore


class TestCacheChatProperties(TestCacheStore):
    async def setUp(self):
        await super().setUp()

        self.dbmain.getAllChatProperties.return_value = AsyncIterator([
            ('kappa', '0'),
            ('keepo', '1'),
        ])

        self.channel = 'megotsthis'
        self.key = f'twitch:{self.channel}:properties'

    async def test_load(self):
        self.assertEqual(
            await self.data.loadChatProperties(self.channel),
            {'kappa': '0', 'keepo': '1'})
        self.assertTrue(self.dbmain.getAllChatProperties.called)
        self.assertIsNotNone(await self.redis.get(self.key))

    async def test(self):
        self.assertEqual(
            await self.data.getChatProperty(self.channel, 'kappa'), '0')
        self.assertTrue(self.dbmain.getAllChatProperties.called)
        self.dbmain.getAllChatProperties.reset_mock()
        self.assertIsNone(
            await self.data.getChatProperty(self.channel, ''))
        self.assertFalse(self.dbmain.getAllChatProperties.called)
        self.assertEqual(
            await self.data.getChatProperties(self.channel, ['kappa']),
            {'kappa': '0'}
        )
        self.assertFalse(self.dbmain.getAllChatProperties.called)
        self.assertIsNotNone(await self.redis.get(self.key))

    async def test_get_property(self):
        self.assertIsNone(
            await self.data.getChatProperty('botgotsthis', ''))

    async def test_get_property_default(self):
        self.assertEqual(
            await self.data.getChatProperty('botgotsthis', '',
                                            default='FrankerZ'),
            'FrankerZ')

    async def test_get_property_default_parse(self):
        self.assertEqual(
            await self.data.getChatProperty('botgotsthis', '',
                                            default='FrankerZ', parse=int),
            'FrankerZ')

    async def test_get_property_existing(self):
        self.assertEqual(
            await self.data.getChatProperty('botgotsthis', 'kappa'),
            '0')

    async def test_get_property_existing_parse(self):
        self.assertEqual(
            await self.data.getChatProperty('botgotsthis', 'kappa', parse=int),
            0)

    async def test_get_property_existing_default_parse(self):
        self.assertEqual(
            await self.data.getChatProperty('botgotsthis', 'kappa',
                                            default='FrankerZ', parse=int),
            0)

    async def test_get_properties(self):
        self.assertEqual(
            await self.data.getChatProperties(
                'botgotsthis', ['frankerz', 'biblethump']),
            {'frankerz': None, 'biblethump': None})

    async def test_get_properties_one(self):
        self.assertEqual(
            await self.data.getChatProperties(
                'botgotsthis', ['kappa', 'frankerz']),
            {'kappa': '0', 'frankerz': None})

    async def test_get_properties_two(self):
        self.assertEqual(
            await self.data.getChatProperties(
                'botgotsthis', ['kappa', 'keepo']),
            {'kappa': '0', 'keepo': '1'})

    async def test_get_properties_default(self):
        self.assertEqual(
            await self.data.getChatProperties(
                'botgotsthis', ['frankerz', 'biblethump'], default=0),
            {'frankerz': 0, 'biblethump': 0})

    async def test_get_properties_default_dict(self):
        self.assertEqual(
            await self.data.getChatProperties(
                'botgotsthis', ['frankerz', 'biblethump'],
                default={'frankerz': 'frankerz', 'biblethump': 'biblethump'}),
            {'frankerz': 'frankerz', 'biblethump': 'biblethump'})

    async def test_get_properties_default_partial(self):
        self.assertEqual(
            await self.data.getChatProperties(
                'botgotsthis', ['frankerz', 'biblethump'],
                default={'frankerz': None}),
            {'frankerz': None})

    async def test_get_properties_parse(self):
        self.assertEqual(
            await self.data.getChatProperties(
                'botgotsthis', ['frankerz', 'biblethump'], parse=int),
            {'frankerz': None, 'biblethump': None})

    async def test_get_properties_parse_default(self):
        self.assertEqual(
            await self.data.getChatProperties(
                'botgotsthis', ['frankerz', 'biblethump'],
                parse=int, default=''),
            {'frankerz': '', 'biblethump': ''})

    async def test_get_properties_parse_values(self):
        self.assertEqual(
            await self.data.getChatProperties(
                'botgotsthis', ['kappa', 'keepo'], parse=int),
            {'kappa': 0, 'keepo': 1})

    async def test_get_properties_parse_dict(self):
        self.assertEqual(
            await self.data.getChatProperties(
                'botgotsthis', ['kappa', 'keepo'],
                parse={'kappa': int, 'keepo': lambda v: int(v) + 0.5}),
            {'kappa': 0, 'keepo': 1.5})

    async def test_get_properties_parse_partial(self):
        self.assertEqual(
            await self.data.getChatProperties(
                'botgotsthis', ['kappa', 'keepo'], parse={'kappa': int}),
            {'kappa': 0, 'keepo': '1'})

    async def test_reset(self):
        await self.data.loadChatProperties(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        await self.data.resetChatProperties(self.channel)
        self.assertIsNone(await self.redis.get(self.key))

    async def test_set(self):
        self.dbmain.setChatProperty.return_value = True
        await self.data.loadChatProperties(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.setChatProperty(self.channel, 'kappa', '1'),
            True)
        self.assertIsNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.setChatProperty.called)

    async def test_set_false(self):
        self.dbmain.setChatProperty.return_value = False
        await self.data.loadChatProperties(self.channel)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertIs(
            await self.data.setChatProperty(self.channel, 'kappa', '1'),
            False)
        self.assertIsNotNone(await self.redis.get(self.key))
        self.assertTrue(self.dbmain.setChatProperty.called)
