from source.data.message import Message
from source.public.custom import params
from tests.unittest.public.test_custom import TestCustomField


class TestCustomParams(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(message=Message('a b c d e'))

    def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(params.fieldParams(self.args))

    def test_zero(self):
        self.args = self.args._replace(field='0')
        self.assertEqual(params.fieldParams(self.args), 'a')

    def test_one(self):
        self.args = self.args._replace(field='1')
        self.assertEqual(params.fieldParams(self.args), 'b')

    def test_default(self):
        self.args = self.args._replace(field='99',
                                       prefix='[', suffix=']')
        self.assertEqual(params.fieldParams(self.args), '')

    def test_prefix(self):
        self.args = self.args._replace(field='0', prefix='[')
        self.assertEqual(params.fieldParams(self.args), '[a')

    def test_prefix_blank(self):
        self.args = self.args._replace(field='0', prefix='')
        self.assertEqual(params.fieldParams(self.args), 'a')

    def test_suffix(self):
        self.args = self.args._replace(field='0', suffix=']')
        self.assertEqual(params.fieldParams(self.args), 'a]')

    def test_suffix_blank(self):
        self.args = self.args._replace(field='0', suffix='')
        self.assertEqual(params.fieldParams(self.args), 'a')

    def test_range(self):
        self.args = self.args._replace(field='1-2')
        self.assertEqual(params.fieldParams(self.args), 'b c')
        self.args = self.args._replace(field='0-2')
        self.assertEqual(params.fieldParams(self.args), 'a b c')

    def test_starting(self):
        self.args = self.args._replace(field='1-')
        self.assertEqual(params.fieldParams(self.args), 'b c d e')
        self.args = self.args._replace(field='0-')
        self.assertEqual(params.fieldParams(self.args), 'a b c d e')

    def test_ending(self):
        self.args = self.args._replace(field='-2')
        self.assertEqual(params.fieldParams(self.args), 'b c')
