from source.data.message import Message
from source.public.custom import query
from tests.unittest.public.test_custom import TestCustomField


class TestCustomQuery(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='query', message=Message('a b c'))

    def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(query.fieldQuery(self.args))

    def test_query(self):
        self.assertEqual(query.fieldQuery(self.args), 'b c')

    def test_caps(self):
        self.args = self.args._replace(field='QUERY')
        self.assertEqual(query.fieldQuery(self.args), 'b c')

    def test_default(self):
        self.args = self.args._replace(message=Message(''),
                                       prefix='[', suffix=']')
        self.assertEqual(query.fieldQuery(self.args), '')

    def test_prefix(self):
        self.args = self.args._replace(prefix='[')
        self.assertEqual(query.fieldQuery(self.args), '[b c')

    def test_prefix_blank(self):
        self.args = self.args._replace(prefix='')
        self.assertEqual(query.fieldQuery(self.args), 'b c')

    def test_suffix(self):
        self.args = self.args._replace(suffix=']')
        self.assertEqual(query.fieldQuery(self.args), 'b c]')

    def test_suffix_blank(self):
        self.args = self.args._replace(suffix='')
        self.assertEqual(query.fieldQuery(self.args), 'b c')
