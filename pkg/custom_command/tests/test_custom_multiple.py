from tests.unittest.base_custom import TestCustomProcess

# Needs to be imported last
from ..custom import multiple


class TestCustomMultiple(TestCustomProcess):
    def setUp(self):
        super().setUp()
        property_return = [True, None]
        self.property_return = property_return
        self.database.getCustomCommandProperty.side_effect = property_return

    async def test(self):
        self.property_return[0] = False
        self.messages[0] = 'Kappa&&KappaHD'
        await multiple.propertyMultipleLines(self.args)
        self.assertEqual(self.messages, ['Kappa&&KappaHD'])

    async def test_split(self):
        self.messages[0] = 'Kappa&&KappaHD'
        await multiple.propertyMultipleLines(self.args)
        self.assertEqual(self.messages, ['Kappa', 'KappaHD'])

    async def test_split_multiple(self):
        self.messages.append('KappaRoss&&KappaPride')
        await multiple.propertyMultipleLines(self.args)
        self.assertEqual(self.messages, ['Kappa', 'KappaRoss', 'KappaPride'])

    async def test_split_delimiter(self):
        self.property_return[1] = '::'
        self.messages[0] = 'Kappa::KappaHD'
        await multiple.propertyMultipleLines(self.args)
        self.assertEqual(self.messages, ['Kappa', 'KappaHD'])
