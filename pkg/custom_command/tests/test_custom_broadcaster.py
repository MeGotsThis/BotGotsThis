from tests.unittest.base_custom import TestCustomField

# Needs to be imported last
from ..custom import broadcaster


class TestCustomBroadcaster(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='broadcaster')

    async def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(await broadcaster.fieldBroadcaster(self.args))

    async def test_broadcaster(self):
        self.assertEqual(await broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis')

    async def test_streamer(self):
        self.args = self.args._replace(field='streamer')
        self.assertEqual(await broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis')

    async def test_broadcaster_caps(self):
        self.args = self.args._replace(field='BROADCASTER')
        self.assertEqual(await broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis')

    async def test_streamer_caps(self):
        self.args = self.args._replace(field='STREAMER')
        self.assertEqual(await broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis')

    async def test_default(self):
        self.args = self.args._replace(channel='', prefix='[', suffix=']')
        self.assertEqual(await broadcaster.fieldBroadcaster(self.args), '')

    async def test_prefix(self):
        self.args = self.args._replace(prefix='[')
        self.assertEqual(await broadcaster.fieldBroadcaster(self.args),
                         '[botgotsthis')

    async def test_prefix_blank(self):
        self.args = self.args._replace(prefix='')
        self.assertEqual(await broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis')

    async def test_suffix(self):
        self.args = self.args._replace(suffix=']')
        self.assertEqual(await broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis]')

    async def test_suffix_blank(self):
        self.args = self.args._replace(suffix='')
        self.assertEqual(await broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis')
