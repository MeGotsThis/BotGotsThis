from source.public.custom import user
from tests.unittest.public.test_custom import TestCustomField


class TestCustomUser(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='user', nick='megotsthis')

    def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(user.fieldUser(self.args))

    def test_user(self):
        self.assertEqual(user.fieldUser(self.args), 'megotsthis')

    def test_nick(self):
        self.args = self.args._replace(field='nick')
        self.assertEqual(user.fieldUser(self.args), 'megotsthis')

    def test_user_caps(self):
        self.args = self.args._replace(field='USER')
        self.assertEqual(user.fieldUser(self.args), 'megotsthis')

    def test_nick_caps(self):
        self.args = self.args._replace(field='NICK')
        self.assertEqual(user.fieldUser(self.args), 'megotsthis')

    def test_default(self):
        self.args = self.args._replace(nick='', prefix='[', suffix=']')
        self.assertEqual(user.fieldUser(self.args), '')

    def test_prefix(self):
        self.args = self.args._replace(prefix='[')
        self.assertEqual(user.fieldUser(self.args), '[megotsthis')

    def test_prefix_blank(self):
        self.args = self.args._replace(prefix='')
        self.assertEqual(user.fieldUser(self.args), 'megotsthis')

    def test_suffix(self):
        self.args = self.args._replace(suffix=']')
        self.assertEqual(user.fieldUser(self.args), 'megotsthis]')

    def test_suffix_blank(self):
        self.args = self.args._replace(suffix='')
        self.assertEqual(user.fieldUser(self.args), 'megotsthis')
