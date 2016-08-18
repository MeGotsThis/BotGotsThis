from source.data.message import Message
from source.public.custom import multiple
from tests.unittest.base_custom import TestCustomProcess


class TestCustomMultiple(TestCustomProcess):
    def setUp(self):
        super().setUp()
        property_return = [True, None]
        self.property_return = property_return
        self.database.getCustomCommandProperty.side_effect = property_return

    def test(self):
        self.property_return[0] = False
        multiple.propertyMultipleLines(self.args)
        self.assertEqual(self.messages, ['Kappa'])

    def test_split(self):
        self.messages[0] = 'Kappa&&KappaHD'
        multiple.propertyMultipleLines(self.args)
        self.assertEqual(self.messages, ['Kappa', 'KappaHD'])

    def test_split_multiple(self):
        self.messages.append('KappaRoss&&KappaPride')
        multiple.propertyMultipleLines(self.args)
        self.assertEqual(self.messages, ['Kappa', 'KappaRoss', 'KappaPride'])

    def test_split_delimiter(self):
        self.property_return[1] = '::'
        self.messages[0] = 'Kappa::KappaHD'
        multiple.propertyMultipleLines(self.args)
        self.assertEqual(self.messages, ['Kappa', 'KappaHD'])
