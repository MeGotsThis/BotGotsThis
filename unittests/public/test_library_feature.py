import unittest
from source.data.message import Message
from source.database import DatabaseBase
from source.public.library import feature
from unittest.mock import ANY, Mock, patch


def send(messages):
    pass


class TestLibraryFeatureFeature(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

        patcher = patch.dict('lists.feature.features')
        self.addCleanup(patcher.stop)
        patcher.start()
        feature.lists.feature.features['feature'] = 'Feature'
        feature.lists.feature.features['none'] = None

        patcher = patch('source.public.library.feature.feature_add',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_add = patcher.start()

        patcher = patch('source.public.library.feature.feature_remove',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_remove = patcher.start()

    def test(self):
        self.mock_add.return_value = True
        self.assertIs(
            feature.feature(self.database, 'botgotsthis',
                            Message('!feature feature'), self.send),
            True)
        self.assertFalse(self.send.called)
        self.mock_add.assert_called_once_with(
            self.database, 'botgotsthis', 'feature', self.send)
        self.assertFalse(self.mock_remove.called)

    def test_add(self):
        self.mock_add.return_value = True
        self.assertIs(
            feature.feature(self.database, 'botgotsthis',
                            Message('!feature feature yes'), self.send),
            True)
        self.assertFalse(self.send.called)
        self.mock_add.assert_called_once_with(
            self.database, 'botgotsthis', 'feature', self.send)
        self.assertFalse(self.mock_remove.called)

    def test_remove(self):
        self.mock_remove.return_value = True
        self.assertIs(
            feature.feature(self.database, 'botgotsthis',
                            Message('!feature feature no'), self.send),
            True)
        self.assertFalse(self.send.called)
        self.mock_remove.assert_called_once_with(
            self.database, 'botgotsthis', 'feature', self.send)
        self.assertFalse(self.mock_add.called)

    def test_not_existing_feature(self):
        self.assertIs(
            feature.feature(self.database, 'botgotsthis',
                            Message('!feature does_not_exist'), self.send),
            True)
        self.send.assert_called_once_with(ANY)
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_remove.called)

    def test_feature_none(self):
        self.assertIs(
            feature.feature(self.database, 'botgotsthis',
                            Message('!feature none'), self.send),
            True)
        self.send.assert_called_once_with(ANY)
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_remove.called)

    def test_bad_param(self):
        self.assertIs(
            feature.feature(self.database, 'botgotsthis',
                            Message('!feature feature Kappa'), self.send),
            True)
        self.send.assert_called_once_with(ANY)
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_remove.called)


class TestLibraryFeatureAdd(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

        patcher = patch.dict('lists.feature.features')
        self.addCleanup(patcher.stop)
        patcher.start()
        feature.lists.feature.features['feature'] = 'Feature'

    def test(self):
        self.database.hasFeature.return_value = False
        self.assertIs(
            feature.feature_add(self.database, 'botgotsthis', 'feature',
                                self.send),
            True)
        self.send.assert_called_once_with(ANY)
        self.database.hasFeature.assert_called_once_with(
            'botgotsthis', 'feature')
        self.database.addFeature.assert_called_once_with(
            'botgotsthis', 'feature')

    def test_existing(self):
        self.database.hasFeature.return_value = True
        self.assertIs(
            feature.feature_add(self.database, 'botgotsthis', 'feature',
                                self.send),
            True)
        self.send.assert_called_once_with(ANY)
        self.database.hasFeature.assert_called_once_with(
            'botgotsthis', 'feature')
        self.assertFalse(self.database.addFeature.called)


class TestLibraryFeatureRemove(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

        patcher = patch.dict('lists.feature.features')
        self.addCleanup(patcher.stop)
        patcher.start()
        feature.lists.feature.features['feature'] = 'Feature'

    def test(self):
        self.database.hasFeature.return_value = True
        self.assertIs(
            feature.feature_remove(self.database, 'botgotsthis', 'feature',
                                   self.send),
            True)
        self.send.assert_called_once_with(ANY)
        self.database.hasFeature.assert_called_once_with(
            'botgotsthis', 'feature')
        self.database.removeFeature.assert_called_once_with(
            'botgotsthis', 'feature')

    def test_existing(self):
        self.database.hasFeature.return_value = False
        self.assertIs(
            feature.feature_remove(self.database, 'botgotsthis', 'feature',
                                   self.send),
            True)
        self.send.assert_called_once_with(ANY)
        self.database.hasFeature.assert_called_once_with(
            'botgotsthis', 'feature')
        self.assertFalse(self.database.removeFeature.called)
