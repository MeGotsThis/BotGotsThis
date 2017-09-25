from lib.data.message import Message
from tests.unittest.base_custom import TestCustomField

# Needs to be imported last
from ..custom import query


class TestCustomQuery(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='query', message=Message('a b c'))

    async def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(await query.fieldQuery(self.args))

    async def test_query(self):
        self.assertEqual(await query.fieldQuery(self.args), 'b c')

    async def test_caps(self):
        self.args = self.args._replace(field='QUERY')
        self.assertEqual(await query.fieldQuery(self.args), 'b c')

    async def test_default(self):
        self.args = self.args._replace(message=Message(''),
                                       prefix='[', suffix=']')
        self.assertEqual(await query.fieldQuery(self.args), '')

    async def test_prefix(self):
        self.args = self.args._replace(prefix='[')
        self.assertEqual(await query.fieldQuery(self.args), '[b c')

    async def test_prefix_blank(self):
        self.args = self.args._replace(prefix='')
        self.assertEqual(await query.fieldQuery(self.args), 'b c')

    async def test_suffix(self):
        self.args = self.args._replace(suffix=']')
        self.assertEqual(await query.fieldQuery(self.args), 'b c]')

    async def test_suffix_blank(self):
        self.args = self.args._replace(suffix='')
        self.assertEqual(await query.fieldQuery(self.args), 'b c')
