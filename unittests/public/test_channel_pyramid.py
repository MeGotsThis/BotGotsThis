from datetime import timedelta
from source.data.message import Message
from source.public.channel import pyramid
from unittest.mock import ANY, patch
from unittests.public.test_channel import TestChannel


class TestChannelPyramid(TestChannel):
    def setUp(self):
        super().setUp()
        self.permissions.broadcaster = False
        self.permissions.globalModerator = False
        self.permissions.chatModerator = False

    @patch('source.public.channel.pyramid.process_pyramid', autospec=True)
    def test_pyramid_false(self, mock_process):
        self.assertIs(pyramid.commandPyramid(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(pyramid.commandPyramid(self.args), False)
        self.assertFalse(mock_process.called)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.pyramid.process_pyramid', autospec=True)
    def test_pyramid(self, mock_process):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        message = Message('!pyramid Kappa')
        self.assertIs(
            pyramid.commandPyramid(self.args._replace(message=message)), True)
        mock_process.assert_called_once_with(ANY, 'Kappa', 5)

    @patch('source.public.channel.pyramid.process_pyramid', autospec=True)
    def test_pyramid_count(self, mock_process):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        message = Message('!pyramid Kappa 20')
        self.assertIs(
            pyramid.commandPyramid(self.args._replace(message=message)), True)
        mock_process.assert_called_once_with(ANY, 'Kappa', 20)

    @patch('source.public.channel.pyramid.process_pyramid', autospec=True)
    def test_pyramid_moderator(self, mock_process):
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        mock_process.return_value = True
        message = Message('!pyramid Kappa')
        self.assertIs(
            pyramid.commandPyramid(self.args._replace(message=message)), True)
        mock_process.assert_called_once_with(ANY, 'Kappa', 3)

    @patch('source.public.channel.pyramid.process_pyramid', autospec=True)
    def test_long_pyramid_false(self, mock_process):
        self.assertIs(pyramid.commandPyramidLong(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(pyramid.commandPyramidLong(self.args), False)
        self.assertFalse(mock_process.called)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.pyramid.process_pyramid', autospec=True)
    def test_long_pyramid(self, mock_process):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        message = Message('!pyramid- Kappa Kappa')
        self.assertIs(
            pyramid.commandPyramidLong(self.args._replace(message=message)),
            True)
        mock_process.assert_called_once_with(ANY, 'Kappa Kappa', 5)

    @patch('source.public.channel.pyramid.process_pyramid', autospec=True)
    def test_long_pyramid_count(self, mock_process):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        message = Message('!pyramid-20 Kappa Kappa')
        self.assertIs(
            pyramid.commandPyramidLong(self.args._replace(message=message)),
            True)
        mock_process.assert_called_once_with(ANY, 'Kappa Kappa', 20)

    @patch('source.public.channel.pyramid.process_pyramid', autospec=True)
    def test_long_pyramid_moderator(self, mock_process):
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        mock_process.return_value = True
        message = Message('!pyramid- Kappa Kappa')
        self.assertIs(
            pyramid.commandPyramidLong(self.args._replace(message=message)),
            True)
        mock_process.assert_called_once_with(ANY, 'Kappa Kappa', 3)

    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process_pyramid(self, mock_timeout, mock_cooldown, mock_config):
        mock_config.messageLimit = 100
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 0), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]), [])

    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process_pyramid_1(self, mock_timeout, mock_cooldown, mock_config):
        mock_config.messageLimit = 100
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 1), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]), ['Kappa'])

    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process_pyramid_2(self, mock_timeout, mock_cooldown, mock_config):
        mock_config.messageLimit = 100
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]),
                         ['Kappa', 'Kappa Kappa', 'Kappa'])

    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process_pyramid_5(self, mock_timeout, mock_cooldown, mock_config):
        mock_config.messageLimit = 300
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 5), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(mock_timeout.called)
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

    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process_pyramid_channel_mod(self, mock_timeout, mock_cooldown,
                                         mock_config):
        mock_config.messageLimit = 300
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.permissions.chatModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        mock_timeout.assert_called_once_with(
            self.database, self.channel, 'botgotsthis', 'Kappa Kappa',
            str(self.args.message), 'pyramid')
        self.assertEqual(list(self.channel.send.call_args[0][0]),
                         ['Kappa', 'Kappa Kappa', 'Kappa'])

    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process_pyramid_broadcaster_limit(
            self, mock_timeout, mock_cooldown, mock_config):
        mock_config.messageLimit = 10000
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa ', 100), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(mock_timeout.called)
        self.assertEqual(
            len(list(self.channel.send.call_args[0][0])), 20 + 20 - 1)

    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process_pyramid_moderator_limit(
            self, mock_timeout, mock_cooldown, mock_config):
        mock_config.messageLimit = 100
        mock_config.spamModeratorCooldown = 30
        mock_cooldown.return_value = False
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_timeout.called)
        mock_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), ANY)
        self.assertEqual(list(self.channel.send.call_args[0][0]),
                         ['Kappa', 'Kappa Kappa', 'Kappa'])

    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process_pyramid_moderator_cooldown(
            self, mock_timeout, mock_cooldown, mock_config):
        mock_config.messageLimit = 100
        mock_config.spamModeratorCooldown = 30
        mock_cooldown.return_value = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 2), False)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(mock_timeout.called)
        mock_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), ANY)

    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process_pyramid_limit(self, mock_timeout, mock_cooldown,
                                   mock_config):
        mock_config.messageLimit = 10
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]), ['Kappa'])

    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('source.public.library.timeout.record_timeout', autospec=True)
    def test_process_pyramid_limit_exact(self, mock_timeout, mock_cooldown,
                                         mock_config):
        mock_config.messageLimit = 11
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]),
                         ['Kappa', 'Kappa Kappa', 'Kappa'])

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    def test_random_pyramid_false(self, mock_cooldown, mock_config,
                                  mock_globals):
        self.assertIs(pyramid.commandRandomPyramid(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(pyramid.commandRandomPyramid(self.args), False)
        mock_globals.emotes = {}
        self.permissionSet['broadcaster'] = True
        self.assertIs(pyramid.commandRandomPyramid(self.args), False)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(self.channel.send.called)

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('random.choice', autospec=True)
    def test_random_pyramid(self, mock_choice, mock_cooldown, mock_config,
                            mock_globals):
        mock_globals.globalEmotes = {
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
        mock_choice.side_effect = [0, 5, 3, 1, 7]
        mock_config.messageLimit = 100
        mock_config.spamModeratorCooldown = 30
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
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

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('random.choice', autospec=True)
    def test_random_pyramid_0(self, mock_choice, mock_cooldown, mock_config,
                              mock_globals):
        mock_globals.globalEmotes = {
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
        mock_choice.side_effect = [0, 5, 3, 1, 7]
        mock_config.messageLimit = 100
        mock_config.spamModeratorCooldown = 30
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid 0')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertEqual( list(self.channel.send.call_args[0][0]), [])

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('random.choice', autospec=True)
    def test_random_pyramid_1(self, mock_choice, mock_cooldown, mock_config,
                              mock_globals):
        mock_globals.globalEmotes = {
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
        mock_choice.side_effect = [0, 5, 3, 1, 7]
        mock_config.messageLimit = 100
        mock_config.spamModeratorCooldown = 30
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid 1')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]), [':)'])

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('random.choice', autospec=True)
    def test_random_pyramid_2(self, mock_choice, mock_cooldown, mock_config,
                              mock_globals):
        mock_globals.globalEmotes = {
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
        mock_choice.side_effect = [0, 5, 3, 1, 7]
        mock_config.messageLimit = 100
        mock_config.spamModeratorCooldown = 30
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid 2')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]),
            [':)', ':) FrankerZ', ':)'])

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('random.choice', autospec=True)
    def test_random_pyramid_broadcaster_limit(
            self, mock_choice, mock_cooldown, mock_config, mock_globals):
        mock_globals.globalEmotes = {
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
        mock_choice.side_effect = [0, 5, 3, 1, 7] * 10
        mock_config.messageLimit = 1000
        mock_config.spamModeratorCooldown = 30
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        message = Message('!rpyramid 50')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertEqual(
            len(list(self.channel.send.call_args[0][0])), 20 + 20 - 1)

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('random.choice', autospec=True)
    def test_random_pyramid_moderator(self, mock_choice, mock_cooldown,
                                      mock_config, mock_globals):
        mock_globals.globalEmotes = {
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
        mock_choice.side_effect = [0, 5, 3, 1, 7]
        mock_config.messageLimit = 100
        mock_config.spamModeratorCooldown = 30
        mock_cooldown.return_value = False
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        mock_cooldown.assert_called_once_with(args, timedelta(seconds=30), ANY)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]),
            [':)',
             ':) FrankerZ',
             ':) FrankerZ PogChamp',
             ':) FrankerZ',
             ':)',
             ])

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('random.choice', autospec=True)
    def test_random_pyramid_moderator_limit(
            self, mock_choice, mock_cooldown, mock_config, mock_globals):
        mock_globals.globalEmotes = {
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
        mock_choice.side_effect = [0, 5, 3, 1, 7]
        mock_config.messageLimit = 100
        mock_config.spamModeratorCooldown = 30
        mock_cooldown.return_value = False
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        message = Message('!rpyramid 10')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        mock_cooldown.assert_called_once_with(args, timedelta(seconds=30), ANY)
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

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('random.choice', autospec=True)
    def test_random_pyramid_moderator_cooldown(
            self, mock_choice, mock_cooldown, mock_config, mock_globals):
        mock_globals.globalEmotes = {
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
        mock_choice.side_effect = [0, 5, 3, 1, 7]
        mock_config.messageLimit = 100
        mock_config.spamModeratorCooldown = 30
        mock_cooldown.return_value = True
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), False)
        self.assertFalse(self.channel.send.called)
        mock_cooldown.assert_called_once_with(args, timedelta(seconds=30), ANY)

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('random.choice', autospec=True)
    def test_random_pyramid_limit(self, mock_choice, mock_cooldown,
                                  mock_config, mock_globals):
        mock_globals.globalEmotes = {
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
        mock_choice.side_effect = [0, 5, 3, 1, 7]
        mock_config.messageLimit = 30
        mock_config.spamModeratorCooldown = 30
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
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

    @patch('bot.globals', autospec=True)
    @patch('bot.config', autospec=True)
    @patch('source.public.library.chat.inCooldown', autospec=True)
    @patch('random.choice', autospec=True)
    def test_random_pyramid_limit_exact(self, mock_choice, mock_cooldown,
                                        mock_config, mock_globals):
        mock_globals.globalEmotes = {
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
        mock_choice.side_effect = [0, 5, 3, 1, 7]
        mock_config.messageLimit = 20
        mock_config.spamModeratorCooldown = 30
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]),
            [':)',
             ':) FrankerZ',
             ':) FrankerZ PogChamp',
             ':) FrankerZ',
             ':)',
             ])
