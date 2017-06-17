from source.data.message import Message
from tests.unittest.base_custom import TestCustomField

# Needs to be imported last
from source.public.custom import params


class TestCustomParams(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(message=Message('a b c d e'))

    async def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(await params.fieldParams(self.args))

    async def test_zero(self):
        self.args = self.args._replace(field='0')
        self.assertEqual(await params.fieldParams(self.args), 'a')

    async def test_one(self):
        self.args = self.args._replace(field='1')
        self.assertEqual(await params.fieldParams(self.args), 'b')

    async def test_default(self):
        self.args = self.args._replace(field='99',
                                       prefix='[', suffix=']')
        self.assertEqual(await params.fieldParams(self.args), '')

    async def test_prefix(self):
        self.args = self.args._replace(field='0', prefix='[')
        self.assertEqual(await params.fieldParams(self.args), '[a')

    async def test_prefix_blank(self):
        self.args = self.args._replace(field='0', prefix='')
        self.assertEqual(await params.fieldParams(self.args), 'a')

    async def test_suffix(self):
        self.args = self.args._replace(field='0', suffix=']')
        self.assertEqual(await params.fieldParams(self.args), 'a]')

    async def test_suffix_blank(self):
        self.args = self.args._replace(field='0', suffix='')
        self.assertEqual(await params.fieldParams(self.args), 'a')

    async def test_range(self):
        self.args = self.args._replace(field='1-2')
        self.assertEqual(await params.fieldParams(self.args), 'b c')
        self.args = self.args._replace(field='0-2')
        self.assertEqual(await params.fieldParams(self.args), 'a b c')

    async def test_starting(self):
        self.args = self.args._replace(field='1-')
        self.assertEqual(await params.fieldParams(self.args), 'b c d e')
        self.args = self.args._replace(field='0-')
        self.assertEqual(await params.fieldParams(self.args), 'a b c d e')

    async def test_ending(self):
        self.args = self.args._replace(field='-2')
        self.assertEqual(await params.fieldParams(self.args), 'b c')
