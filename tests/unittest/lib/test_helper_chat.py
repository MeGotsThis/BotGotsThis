from datetime import datetime, timedelta

import asynctest
from asynctest.mock import MagicMock, Mock, PropertyMock, patch

from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from lib.cache import CacheStore
from lib.data import ChatCommandArgs
from lib.data.message import Message
from lib.data.permissions import ChatPermissionSet
from lib.database import DatabaseMain
from lib.helper import chat


class TestLibraryChat(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.tags = IrcMessageTags()
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.data = Mock(spec=CacheStore)
        self.database = Mock(spec=DatabaseMain)
        self.permissions = MagicMock(spec=ChatPermissionSet)
        self.args = ChatCommandArgs(
            self.data, self.database, self.channel, self.tags, 'botgotsthis',
            Message(''), self.permissions, self.now)

    @asynctest.fail_on(unused_loop=False)
    def test_send(self):
        self.assertIs(chat.send(self.channel), self.channel.send)
        chat.send(self.channel)('Kappa')
        self.channel.send.assert_called_once_with('Kappa')

    @asynctest.fail_on(unused_loop=False)
    def test_send_priority(self):
        chat.sendPriority(self.channel, 0)('Kappa')
        self.channel.send.assert_called_once_with('Kappa', priority=0)

    async def test_permission(self):
        self.permissions.__getitem__.return_value = True

        @chat.permission('')
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_permission_not(self):
        self.permissions.__getitem__.return_value = False

        @chat.permission('')
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_not_permission(self):
        self.permissions.__getitem__.return_value = False

        @chat.not_permission('')
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_not_permission_not(self):
        self.permissions.__getitem__.return_value = True

        @chat.not_permission('')
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_owner_channel(self):
        ownerProperty = PropertyMock(return_value=False)
        type(self.permissions).inOwnerChannel = ownerProperty

        @chat.ownerChannel
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        ownerProperty.assert_called_once_with()

    async def test_owner_channel_not(self):
        ownerProperty = PropertyMock(return_value=False)
        type(self.permissions).inOwnerChannel = ownerProperty

        @chat.ownerChannel
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        ownerProperty.assert_called_once_with()

    async def test_feature(self):
        self.database.hasFeature.return_value = True

        @chat.feature('')
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')

    async def test_feature_not(self):
        self.database.hasFeature.return_value = False

        @chat.feature('')
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')

    async def test_not_feature(self):
        self.database.hasFeature.return_value = False

        @chat.not_feature('')
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')

    async def test_not_feature_not(self):
        self.database.hasFeature.return_value = True

        @chat.not_feature('')
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')

    async def test_permission_feature(self):
        self.database.hasFeature.return_value = True
        self.permissions.__getitem__.return_value = True

        @chat.permission_feature(('', ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_permission_feature_not_permission(self):
        self.database.hasFeature.return_value = True
        self.permissions.__getitem__.return_value = False

        @chat.permission_feature(('', ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)

    async def test_permission_feature_not_feature(self):
        self.database.hasFeature.return_value = False
        self.permissions.__getitem__.return_value = True

        @chat.permission_feature(('', ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)

    async def test_permission_feature_not(self):
        self.database.hasFeature.return_value = False
        self.permissions.__getitem__.return_value = False

        @chat.permission_feature(('', ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)

    async def test_permission_feature_none_permission(self):
        self.database.hasFeature.return_value = True

        @chat.permission_feature((None, ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')
        self.permissions.__getitem__.assert_not_called()

    async def test_permission_feature_none_feature(self):
        self.permissions.__getitem__.return_value = True

        @chat.permission_feature(('', None))
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.database.hasFeature.assert_not_called()
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_permission_feature_none_permission_not(self):
        self.database.hasFeature.return_value = False

        @chat.permission_feature((None, ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')
        self.permissions.__getitem__.assert_not_called()

    async def test_permission_feature_none_feature_not(self):
        self.permissions.__getitem__.return_value = False

        @chat.permission_feature(('', None))
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        self.database.hasFeature.assert_not_called()
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_permission_feature_none_permission_feature(self):
        @chat.permission_feature((None, None))
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.database.hasFeature.assert_not_called()
        self.permissions.__getitem__.assert_not_called()

    async def test_permission_feature_multiple(self):
        self.database.hasFeature.side_effect = [False, True]
        self.permissions.__getitem__.side_effect = [False, True]

        @chat.permission_feature(('', ''), ('', ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)

    async def test_permission_feature_multiple_not(self):
        self.database.hasFeature.side_effect = [False, True]
        self.permissions.__getitem__.side_effect = [True, False]

        @chat.permission_feature(('', ''), ('', ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)

    async def test_permission_not_feature(self):
        self.database.hasFeature.return_value = False
        self.permissions.__getitem__.return_value = True

        @chat.permission_not_feature(('', ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_permission_not_feature_not_permission(self):
        self.database.hasFeature.return_value = False
        self.permissions.__getitem__.return_value = False

        @chat.permission_not_feature(('', ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)

    async def test_permission_not_feature_not_feature(self):
        self.database.hasFeature.return_value = True
        self.permissions.__getitem__.return_value = True

        @chat.permission_not_feature(('', ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)

    async def test_permission_not_feature_not(self):
        self.database.hasFeature.return_value = True
        self.permissions.__getitem__.return_value = False

        @chat.permission_not_feature(('', ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)

    async def test_permission_not_feature_none_permission(self):
        self.database.hasFeature.return_value = False

        @chat.permission_not_feature((None, ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')
        self.permissions.__getitem__.assert_not_called()

    async def test_permission_not_feature_none_feature(self):
        self.permissions.__getitem__.return_value = True

        @chat.permission_not_feature(('', None))
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.database.hasFeature.assert_not_called()
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_permission_not_feature_none_permission_not(self):
        self.database.hasFeature.return_value = True

        @chat.permission_not_feature((None, ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')
        self.permissions.__getitem__.assert_not_called()

    async def test_permission_not_feature_none_feature_not(self):
        self.permissions.__getitem__.return_value = False

        @chat.permission_not_feature(('', None))
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        self.database.hasFeature.assert_not_called()
        self.permissions.__getitem__.assert_called_once_with('')

    async def test_permission_not_feature_none_permission_feature(self):
        @chat.permission_not_feature((None, None))
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.database.hasFeature.assert_not_called()
        self.permissions.__getitem__.assert_not_called()

    async def test_permission_not_feature_multiple(self):
        self.database.hasFeature.side_effect = [True, False]
        self.permissions.__getitem__.side_effect = [False, True]

        @chat.permission_not_feature(('', ''), ('', ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)

    async def test_permission_not_feature_multiple_not(self):
        self.database.hasFeature.side_effect = [True, False]
        self.permissions.__getitem__.side_effect = [True, False]

        @chat.permission_not_feature(('', ''), ('', ''))
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)

    @patch('lib.helper.chat.inCooldown')
    async def test_cooldown(self, mock_inCooldown):
        mock_inCooldown.return_value = False

        @chat.cooldown(timedelta(minutes=1), '')
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)
        self.assertTrue(mock_inCooldown.called)

    @patch('lib.helper.chat.inCooldown')
    async def test_cooldown_not(self, mock_inCooldown):
        mock_inCooldown.return_value = True

        @chat.cooldown(timedelta(minutes=1), '')
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)
        self.assertTrue(mock_inCooldown.called)

    @asynctest.fail_on(unused_loop=False)
    def test_in_cooldown(self):
        sessionData = {}
        self.channel.sessionData = sessionData
        self.assertIs(
            chat.inCooldown(self.args, timedelta(hours=1), ''), False)
        self.assertIn('', sessionData)
        self.assertEqual(sessionData[''], self.now)

    @asynctest.fail_on(unused_loop=False)
    def test_in_cooldown_existing(self):
        sessionData = {'': self.now - timedelta(hours=1)}
        self.channel.sessionData = sessionData
        self.assertIs(
            chat.inCooldown(self.args, timedelta(hours=1), ''), False)
        self.assertIn('', sessionData)
        self.assertEqual(sessionData[''], self.now)

    @asynctest.fail_on(unused_loop=False)
    def test_in_cooldown_recent(self):
        sessionData = {'': self.now - timedelta(seconds=1)}
        self.channel.sessionData = sessionData
        self.assertIs(
            chat.inCooldown(self.args, timedelta(hours=1), ''), True)
        self.assertIn('', sessionData)
        self.assertEqual(sessionData[''], self.now - timedelta(seconds=1))

    @asynctest.fail_on(unused_loop=False)
    def test_in_cooldown_level_override(self):
        sessionData = {'': self.now - timedelta(seconds=1)}
        self.channel.sessionData = sessionData
        self.permissions.__getitem__.return_value = True
        self.assertIs(
            chat.inCooldown(self.args, timedelta(hours=1), '', ''), False)
        self.assertIn('', sessionData)
        self.assertEqual(sessionData[''], self.now)

    @asynctest.fail_on(unused_loop=False)
    def test_in_user_cooldown(self):
        sessionData = {}
        self.channel.sessionData = sessionData
        self.assertIs(
            chat.in_user_cooldown(self.args, timedelta(hours=1), ''), False)
        self.assertIn('', sessionData)
        self.assertIn('botgotsthis', sessionData[''])
        self.assertEqual(sessionData['']['botgotsthis'], self.now)

    @asynctest.fail_on(unused_loop=False)
    def test_in_user_cooldown_existing(self):
        sessionData = {'': {'botgotsthis': self.now - timedelta(hours=1)}}
        self.channel.sessionData = sessionData
        self.assertIs(
            chat.in_user_cooldown(self.args, timedelta(hours=1), ''), False)
        self.assertIn('', sessionData)
        self.assertIn('botgotsthis', sessionData[''])
        self.assertEqual(sessionData['']['botgotsthis'], self.now)

    @asynctest.fail_on(unused_loop=False)
    def test_in_user_cooldown_recent(self):
        sessionData = {'': {'botgotsthis': self.now - timedelta(seconds=1)}}
        self.channel.sessionData = sessionData
        self.assertIs(
            chat.in_user_cooldown(self.args, timedelta(hours=1), ''), True)
        self.assertIn('', sessionData)
        self.assertIn('botgotsthis', sessionData[''])
        self.assertEqual(sessionData['']['botgotsthis'],
                         self.now - timedelta(seconds=1))

    @asynctest.fail_on(unused_loop=False)
    def test_in_user_cooldown_level_override(self):
        sessionData = {'': {'botgotsthis': self.now - timedelta(seconds=1)}}
        self.channel.sessionData = sessionData
        self.permissions.__getitem__.return_value = True
        self.assertIs(
            chat.in_user_cooldown(self.args, timedelta(hours=1), '', ''),
            False)
        self.assertIn('', sessionData)
        self.assertIn('botgotsthis', sessionData[''])
        self.assertEqual(sessionData['']['botgotsthis'], self.now)

    async def test_min_args(self):
        @chat.min_args(0)
        async def t(args):
            return True
        self.assertIs(await t(self.args), True)

    async def test_min_args_not_enough(self):
        @chat.min_args(1)
        async def t(args):
            return True
        self.assertIs(await t(self.args), False)

    async def test_min_args_not_return(self):
        @chat.min_args(1, _return=True)
        async def t(args):
            return False
        self.assertIs(await t(self.args), True)

    async def test_min_args_not_reason(self):
        @chat.min_args(1, reason='Kappa')
        async def t(args):
            return False
        await t(self.args)
        self.channel.send.assert_called_once_with('Kappa')
