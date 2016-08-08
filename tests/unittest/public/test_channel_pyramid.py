from datetime import timedelta
from unittest.mock import ANY, patch

from source.data.message import Message
from source.public.channel import pyramid
from tests.unittest.base_channel import TestChannel


class TestChannelPyramid(TestChannel):
    def setUp(self):
        super().setUp()
        self.permissions.broadcaster = False
        self.permissions.globalModerator = False
        self.permissions.chatModerator = False

        patcher = patch('source.public.channel.pyramid.process_pyramid',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_process = patcher.start()

    def test_pyramid_false(self):
        self.assertIs(pyramid.commandPyramid(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(pyramid.commandPyramid(self.args), False)
        self.assertFalse(self.mock_process.called)
        self.assertFalse(self.channel.send.called)

    def test_pyramid(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!pyramid Kappa')
        self.assertIs(
            pyramid.commandPyramid(self.args._replace(message=message)), True)
        self.mock_process.assert_called_once_with(ANY, 'Kappa', 5)

    def test_pyramid_count(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!pyramid Kappa 20')
        self.assertIs(
            pyramid.commandPyramid(self.args._replace(message=message)), True)
        self.mock_process.assert_called_once_with(ANY, 'Kappa', 20)

    def test_pyramid_moderator(self):
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        self.mock_process.return_value = True
        message = Message('!pyramid Kappa')
        self.assertIs(
            pyramid.commandPyramid(self.args._replace(message=message)), True)
        self.mock_process.assert_called_once_with(ANY, 'Kappa', 3)

    def test_long_pyramid_false(self):
        self.assertIs(pyramid.commandPyramidLong(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(pyramid.commandPyramidLong(self.args), False)
        self.assertFalse(self.mock_process.called)
        self.assertFalse(self.channel.send.called)

    def test_long_pyramid(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!pyramid- Kappa Kappa')
        self.assertIs(
            pyramid.commandPyramidLong(self.args._replace(message=message)),
            True)
        self.mock_process.assert_called_once_with(ANY, 'Kappa Kappa', 5)

    def test_long_pyramid_count(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!pyramid-20 Kappa Kappa')
        self.assertIs(
            pyramid.commandPyramidLong(self.args._replace(message=message)),
            True)
        self.mock_process.assert_called_once_with(ANY, 'Kappa Kappa', 20)

    def test_long_pyramid_moderator(self):
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        self.mock_process.return_value = True
        message = Message('!pyramid- Kappa Kappa')
        self.assertIs(
            pyramid.commandPyramidLong(self.args._replace(message=message)),
            True)
        self.mock_process.assert_called_once_with(ANY, 'Kappa Kappa', 3)


class TestChannelProcessPyramid(TestChannel):
    def setUp(self):
        super().setUp()
        self.permissions.broadcaster = False
        self.permissions.globalModerator = False
        self.permissions.chatModerator = False

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.messageLimit = 100
        self.mock_config.spamModeratorCooldown = 30

        patcher = patch('source.public.library.chat.inCooldown', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_cooldown = patcher.start()

        patcher = patch('source.public.library.timeout.record_timeout',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_timeout = patcher.start()

    def test(self):
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 0), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]), [])

    def test_1(self):
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 1), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]), ['Kappa'])

    def test_2(self):
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]),
                         ['Kappa', 'Kappa Kappa', 'Kappa'])

    def test_5(self):
        self.mock_config.messageLimit = 300
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 5), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]),
            ['Kappa',
             'Kappa Kappa',
             'Kappa Kappa Kappa',
             'Kappa Kappa Kappa Kappa',
             'Kappa Kappa Kappa Kappa Kappa',
             'Kappa Kappa Kappa Kappa',
             'Kappa Kappa Kappa',
             'Kappa Kappa',
             'Kappa'])

    def test_channel_mod(self):
        self.mock_config.messageLimit = 300
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.permissions.chatModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.mock_timeout.assert_called_once_with(
            self.database, self.channel, 'botgotsthis', 'Kappa Kappa',
            str(self.args.message), 'pyramid')
        self.assertEqual(list(self.channel.send.call_args[0][0]),
                         ['Kappa', 'Kappa Kappa', 'Kappa'])

    def test_broadcaster_limit(self):
        self.mock_config.messageLimit = 10000
        self.permissions.broadcaster = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa ', 100), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)
        self.assertEqual(
            len(list(self.channel.send.call_args[0][0])), 20 + 20 - 1)

    def test_moderator_limit(self):
        self.mock_config.messageLimit = 100
        self.mock_cooldown.return_value = False
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_timeout.called)
        self.mock_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), ANY)
        self.assertEqual(list(self.channel.send.call_args[0][0]),
                         ['Kappa', 'Kappa Kappa', 'Kappa'])

    def test_moderator_cooldown(self):
        self.mock_config.messageLimit = 100
        self.mock_cooldown.return_value = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 2), False)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.mock_timeout.called)
        self.mock_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), ANY)

    def test_limit(self):
        self.mock_config.messageLimit = 10
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]), ['Kappa'])

    def test_limit_exact(self):
        self.mock_config.messageLimit = 11
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]),
                         ['Kappa', 'Kappa Kappa', 'Kappa'])


class TestChannelRandomPyramid(TestChannel):
    def setUp(self):
        super().setUp()
        self.permissions.broadcaster = False
        self.permissions.globalModerator = False
        self.permissions.chatModerator = False

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.globalEmotes = {
            0: ':)',
            1: 'Kappa',
            2: 'KevinTurtle',
            3: 'PogChamp',
            4: 'Kreygasm',
            5: 'FrankerZ',
            6: 'PraiseIt',
            7: 'PJSalt',
            8: 'BibleThump',
            9: 'ResidentSleeper',
            }

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.messageLimit = 100
        self.mock_config.spamModeratorCooldown = 30

        patcher = patch('source.public.library.chat.inCooldown', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_cooldown = patcher.start()
        self.mock_cooldown.return_value = False

        patcher = patch('random.choice', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_choice = patcher.start()
        self.mock_choice.side_effect = [0, 5, 3, 1, 7]

    def test_false(self):
        self.assertIs(pyramid.commandRandomPyramid(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(pyramid.commandRandomPyramid(self.args), False)
        self.mock_globals.globalEmotes = {}
        self.permissionSet['broadcaster'] = True
        self.assertIs(pyramid.commandRandomPyramid(self.args), False)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.channel.send.called)

    def test(self):
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]),
            [':)',
             ':) FrankerZ',
             ':) FrankerZ PogChamp',
             ':) FrankerZ PogChamp Kappa',
             ':) FrankerZ PogChamp Kappa PJSalt',
             ':) FrankerZ PogChamp Kappa',
             ':) FrankerZ PogChamp',
             ':) FrankerZ',
             ':)',
             ])

    def test_0(self):
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid 0')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]), [])

    def test_1(self):
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid 1')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]), [':)'])

    def test_2(self):
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid 2')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]),
            [':)', ':) FrankerZ', ':)'])

    def test_broadcaster_limit(self):
        self.mock_choice.side_effect = [0, 5, 3, 1, 7] * 10
        self.mock_config.messageLimit = 1000
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        message = Message('!rpyramid 50')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertEqual(
            len(list(self.channel.send.call_args[0][0])), 20 + 20 - 1)

    def test_moderator(self):
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.mock_cooldown.assert_called_once_with(
            args, timedelta(seconds=30), ANY)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]),
            [':)',
             ':) FrankerZ',
             ':) FrankerZ PogChamp',
             ':) FrankerZ',
             ':)',
             ])

    def test_moderator_limit(self):
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        message = Message('!rpyramid 10')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.mock_cooldown.assert_called_once_with(
            args, timedelta(seconds=30), ANY)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]),
            [':)',
             ':) FrankerZ',
             ':) FrankerZ PogChamp',
             ':) FrankerZ PogChamp Kappa',
             ':) FrankerZ PogChamp Kappa PJSalt',
             ':) FrankerZ PogChamp Kappa',
             ':) FrankerZ PogChamp',
             ':) FrankerZ',
             ':)',
             ])

    def test_moderator_cooldown(self):
        self.mock_cooldown.return_value = True
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), False)
        self.assertFalse(self.channel.send.called)
        self.mock_cooldown.assert_called_once_with(
            args, timedelta(seconds=30), ANY)

    def test_limit(self):
        self.mock_config.messageLimit = 30
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]),
            [':)',
             ':) FrankerZ',
             ':) FrankerZ PogChamp',
             ':) FrankerZ PogChamp Kappa',
             ':) FrankerZ PogChamp',
             ':) FrankerZ',
             ':)',
             ])

    def test_limit_exact(self):
        self.mock_config.messageLimit = 20
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]),
            [':)',
             ':) FrankerZ',
             ':) FrankerZ PogChamp',
             ':) FrankerZ',
             ':)',
             ])
