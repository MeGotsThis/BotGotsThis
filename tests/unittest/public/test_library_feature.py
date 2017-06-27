import asynctest

import bot  # noqa: F401

from asynctest.mock import Mock, patch

from source.data.message import Message
from source.database import DatabaseMain
from source.public.library import feature
from tests.unittest.mock_class import StrContains


def send(messages):
    pass


class TestLibraryFeatureFeature(asynctest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseMain)
        self.send = Mock(spec=send)

        patcher = patch('lists.feature')
        self.addCleanup(patcher.stop)
        self.mock_feature = patcher.start()
        self.mock_feature.features.return_value = {
            'feature': 'Feature',
            'none': None
            }

        patcher = patch('source.public.library.feature.feature_add')
        self.addCleanup(patcher.stop)
        self.mock_add = patcher.start()

        patcher = patch('source.public.library.feature.feature_remove')
        self.addCleanup(patcher.stop)
        self.mock_remove = patcher.start()

    async def test(self):
        self.mock_add.return_value = True
        self.assertIs(
            await feature.feature(self.database, 'botgotsthis',
                                  Message('!feature feature'), self.send),
            True)
        self.assertFalse(self.send.called)
        self.mock_add.assert_called_once_with(
            self.database, 'botgotsthis', 'feature', self.send)
        self.assertFalse(self.mock_remove.called)

    async def test_add(self):
        self.mock_add.return_value = True
        self.assertIs(
            await feature.feature(self.database, 'botgotsthis',
                                  Message('!feature feature yes'), self.send),
            True)
        self.assertFalse(self.send.called)
        self.mock_add.assert_called_once_with(
            self.database, 'botgotsthis', 'feature', self.send)
        self.assertFalse(self.mock_remove.called)

    async def test_remove(self):
        self.mock_remove.return_value = True
        self.assertIs(
            await feature.feature(self.database, 'botgotsthis',
                                  Message('!feature feature no'), self.send),
            True)
        self.assertFalse(self.send.called)
        self.mock_remove.assert_called_once_with(
            self.database, 'botgotsthis', 'feature', self.send)
        self.assertFalse(self.mock_add.called)

    async def test_not_existing_feature(self):
        self.assertIs(
            await feature.feature(self.database, 'botgotsthis',
                                  Message('!feature does_not_exist'),
                                  self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('feature', 'does_not_exist'))
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_remove.called)

    async def test_feature_none(self):
        self.assertIs(
            await feature.feature(self.database, 'botgotsthis',
                                  Message('!feature none'), self.send),
            True)
        self.send.assert_called_once_with(StrContains('feature', 'none'))
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_remove.called)

    async def test_bad_param(self):
        self.assertIs(
            await feature.feature(self.database, 'botgotsthis',
                                  Message('!feature feature Kappa'),
                                  self.send),
            True)
        self.send.assert_called_once_with(StrContains('parameter', 'kappa'))
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_remove.called)


class TestLibraryFeatureAdd(asynctest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseMain)
        self.send = Mock(spec=send)

        patcher = patch('lists.feature')
        self.addCleanup(patcher.stop)
        self.mock_feature = patcher.start()
        self.mock_feature.features.return_value = {'feature': 'Feature'}

    async def test(self):
        self.database.hasFeature.return_value = False
        self.assertIs(
            await feature.feature_add(self.database, 'botgotsthis', 'feature',
                                      self.send),
            True)
        self.send.assert_called_once_with(StrContains('Feature', 'enable'))
        self.database.hasFeature.assert_called_once_with(
            'botgotsthis', 'feature')
        self.database.addFeature.assert_called_once_with(
            'botgotsthis', 'feature')

    async def test_existing(self):
        self.database.hasFeature.return_value = True
        self.assertIs(
            await feature.feature_add(self.database, 'botgotsthis', 'feature',
                                      self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('Feature', 'already', 'enable'))
        self.database.hasFeature.assert_called_once_with(
            'botgotsthis', 'feature')
        self.assertFalse(self.database.addFeature.called)


class TestLibraryFeatureRemove(asynctest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseMain)
        self.send = Mock(spec=send)

        patcher = patch('lists.feature')
        self.addCleanup(patcher.stop)
        self.mock_feature = patcher.start()
        self.mock_feature.features.return_value = {'feature': 'Feature'}

    async def test(self):
        self.database.hasFeature.return_value = True
        self.assertIs(
            await feature.feature_remove(self.database, 'botgotsthis',
                                         'feature', self.send),
            True)
        self.send.assert_called_once_with(StrContains('Feature', 'disable'))
        self.database.hasFeature.assert_called_once_with(
            'botgotsthis', 'feature')
        self.database.removeFeature.assert_called_once_with(
            'botgotsthis', 'feature')

    async def test_existing(self):
        self.database.hasFeature.return_value = False
        self.assertIs(
            await feature.feature_remove(self.database, 'botgotsthis',
                                         'feature', self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('Feature', 'not', 'enable'))
        self.database.hasFeature.assert_called_once_with(
            'botgotsthis', 'feature')
        self.assertFalse(self.database.removeFeature.called)
