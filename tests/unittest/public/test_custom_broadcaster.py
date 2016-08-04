from source.public.custom import broadcaster
from tests.unittest.public.test_custom import TestCustomField


class TestCustomBroadcaster(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='broadcaster')

    def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(broadcaster.fieldBroadcaster(self.args))

    def test_broadcaster(self):
        self.assertEqual(broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis')

    def test_streamer(self):
        self.args = self.args._replace(field='streamer')
        self.assertEqual(broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis')

    def test_broadcaster_caps(self):
        self.args = self.args._replace(field='BROADCASTER')
        self.assertEqual(broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis')

    def test_streamer_caps(self):
        self.args = self.args._replace(field='STREAMER')
        self.assertEqual(broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis')

    def test_default(self):
        self.args = self.args._replace(channel='', prefix='[', suffix=']')
        self.assertEqual(broadcaster.fieldBroadcaster(self.args), '')

    def test_prefix(self):
        self.args = self.args._replace(prefix='[')
        self.assertEqual(broadcaster.fieldBroadcaster(self.args),
                         '[botgotsthis')

    def test_prefix_blank(self):
        self.args = self.args._replace(prefix='')
        self.assertEqual(broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis')

    def test_suffix(self):
        self.args = self.args._replace(suffix=']')
        self.assertEqual(broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis]')

    def test_suffix_blank(self):
        self.args = self.args._replace(suffix='')
        self.assertEqual(broadcaster.fieldBroadcaster(self.args),
                         'botgotsthis')
