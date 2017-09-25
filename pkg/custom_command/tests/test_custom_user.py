from tests.unittest.base_custom import TestCustomField

# Needs to be imported last
from ..custom import user


class TestCustomUser(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='user', nick='megotsthis')

    async def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(await user.fieldUser(self.args))

    async def test_user(self):
        self.assertEqual(await user.fieldUser(self.args), 'megotsthis')

    async def test_nick(self):
        self.args = self.args._replace(field='nick')
        self.assertEqual(await user.fieldUser(self.args), 'megotsthis')

    async def test_user_caps(self):
        self.args = self.args._replace(field='USER')
        self.assertEqual(await user.fieldUser(self.args), 'megotsthis')

    async def test_nick_caps(self):
        self.args = self.args._replace(field='NICK')
        self.assertEqual(await user.fieldUser(self.args), 'megotsthis')

    async def test_default(self):
        self.args = self.args._replace(nick='', prefix='[', suffix=']')
        self.assertEqual(await user.fieldUser(self.args), '')

    async def test_prefix(self):
        self.args = self.args._replace(prefix='[')
        self.assertEqual(await user.fieldUser(self.args), '[megotsthis')

    async def test_prefix_blank(self):
        self.args = self.args._replace(prefix='')
        self.assertEqual(await user.fieldUser(self.args), 'megotsthis')

    async def test_suffix(self):
        self.args = self.args._replace(suffix=']')
        self.assertEqual(await user.fieldUser(self.args), 'megotsthis]')

    async def test_suffix_blank(self):
        self.args = self.args._replace(suffix='')
        self.assertEqual(await user.fieldUser(self.args), 'megotsthis')
