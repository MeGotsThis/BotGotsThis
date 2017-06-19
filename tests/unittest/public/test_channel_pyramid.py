from datetime import timedelta

from asynctest.mock import patch

from source.data.message import Message
from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import IterableMatch, StrContains

# Needs to be imported last
from source.public.channel import pyramid


class TestChannelPyramid(TestChannel):
    def setUp(self):
        super().setUp()
        self.permissions.broadcaster = False
        self.permissions.globalModerator = False
        self.permissions.chatModerator = False

        patcher = patch('source.public.channel.pyramid.process_pyramid')
        self.addCleanup(patcher.stop)
        self.mock_process = patcher.start()

    async def test_pyramid_false(self):
        self.assertIs(await pyramid.commandPyramid(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(await pyramid.commandPyramid(self.args), False)
        self.assertFalse(self.mock_process.called)
        self.assertFalse(self.channel.send.called)

    async def test_pyramid(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!pyramid Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandPyramid(args), True)
        self.mock_process.assert_called_once_with(args, 'Kappa', 5)

    async def test_pyramid_count(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!pyramid Kappa 20')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandPyramid(args), True)
        self.mock_process.assert_called_once_with(args, 'Kappa', 20)

    async def test_pyramid_moderator(self):
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        self.mock_process.return_value = True
        message = Message('!pyramid Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandPyramid(args), True)
        self.mock_process.assert_called_once_with(args, 'Kappa', 3)

    async def test_long_pyramid_false(self):
        self.assertIs(await pyramid.commandPyramidLong(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(await pyramid.commandPyramidLong(self.args), False)
        self.assertFalse(self.mock_process.called)
        self.assertFalse(self.channel.send.called)

    async def test_long_pyramid(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!pyramid- Kappa Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandPyramidLong(args), True)
        self.mock_process.assert_called_once_with(args, 'Kappa Kappa', 5)

    async def test_long_pyramid_count(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!pyramid-20 Kappa Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandPyramidLong(args), True)
        self.mock_process.assert_called_once_with(args, 'Kappa Kappa', 20)

    async def test_long_pyramid_moderator(self):
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        self.mock_process.return_value = True
        message = Message('!pyramid- Kappa Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandPyramidLong(args), True)
        self.mock_process.assert_called_once_with(args, 'Kappa Kappa', 3)


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

        patcher = patch('source.public.library.timeout.record_timeout')
        self.addCleanup(patcher.stop)
        self.mock_timeout = patcher.start()

    async def test(self):
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(await pyramid.process_pyramid(self.args, 'Kappa', 0), True)
        self.channel.send.assert_called_once_with(IterableMatch(), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_1(self):
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(await pyramid.process_pyramid(self.args, 'Kappa', 1), True)
        self.channel.send.assert_called_once_with(IterableMatch('Kappa'), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_2(self):
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(await pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(
            IterableMatch('Kappa', 'Kappa Kappa', 'Kappa'), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_5(self):
        self.mock_config.messageLimit = 300
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(await pyramid.process_pyramid(self.args, 'Kappa', 5), True)
        self.channel.send.assert_called_once_with(
            IterableMatch('Kappa',
                          'Kappa Kappa',
                          'Kappa Kappa Kappa',
                          'Kappa Kappa Kappa Kappa',
                          'Kappa Kappa Kappa Kappa Kappa',
                          'Kappa Kappa Kappa Kappa',
                          'Kappa Kappa Kappa',
                          'Kappa Kappa',
                          'Kappa'), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_channel_mod(self):
        self.mock_config.messageLimit = 300
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.permissions.chatModerator = True
        self.assertIs(await pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(
            IterableMatch('Kappa', 'Kappa Kappa', 'Kappa'), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.mock_timeout.assert_called_once_with(
            self.channel, 'botgotsthis', 'Kappa Kappa',
            str(self.args.message), 'pyramid')

    async def test_broadcaster_limit(self):
        self.mock_config.messageLimit = 10000
        self.permissions.broadcaster = True
        self.assertIs(await pyramid.process_pyramid(self.args, 'Kappa ', 100), True)
        self.channel.send.assert_called_once_with(
            IterableMatch(*([StrContains()] * (20 + 20 - 1))), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_moderator_limit(self):
        self.mock_config.messageLimit = 100
        self.mock_cooldown.return_value = False
        self.assertIs(await pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(
            IterableMatch('Kappa', 'Kappa Kappa', 'Kappa'), -1)
        self.assertFalse(self.mock_timeout.called)
        self.mock_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), 'modPyramid')

    async def test_moderator_cooldown(self):
        self.mock_config.messageLimit = 100
        self.mock_cooldown.return_value = True
        self.assertIs(await pyramid.process_pyramid(self.args, 'Kappa', 2), False)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.mock_timeout.called)
        self.mock_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), 'modPyramid')

    async def test_limit(self):
        self.mock_config.messageLimit = 10
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(await pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(IterableMatch('Kappa'), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_limit_exact(self):
        self.mock_config.messageLimit = 11
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(await pyramid.process_pyramid(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(
            IterableMatch('Kappa', 'Kappa Kappa', 'Kappa'), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)


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

    async def test_false(self):
        self.assertIs(await pyramid.commandRandomPyramid(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(await pyramid.commandRandomPyramid(self.args), False)
        self.mock_globals.globalEmotes = {}
        self.permissionSet['broadcaster'] = True
        self.assertIs(await pyramid.commandRandomPyramid(self.args), False)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.channel.send.called)

    async def test(self):
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(
            IterableMatch(':)',
                          ':) FrankerZ',
                          ':) FrankerZ PogChamp',
                          ':) FrankerZ PogChamp Kappa',
                          ':) FrankerZ PogChamp Kappa PJSalt',
                          ':) FrankerZ PogChamp Kappa',
                          ':) FrankerZ PogChamp',
                          ':) FrankerZ',
                          ':)'), -1)
        self.assertFalse(self.mock_cooldown.called)

    async def test_0(self):
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid 0')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(IterableMatch(), -1)
        self.assertFalse(self.mock_cooldown.called)

    async def test_1(self):
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid 1')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(IterableMatch(':)'), -1)
        self.assertFalse(self.mock_cooldown.called)

    async def test_2(self):
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid 2')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(
            IterableMatch(':)',
                          ':) FrankerZ',
                          ':)'), -1)
        self.assertFalse(self.mock_cooldown.called)

    async def test_broadcaster_limit(self):
        self.mock_choice.side_effect = [0, 5, 3, 1, 7] * 10
        self.mock_config.messageLimit = 1000
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        message = Message('!rpyramid 50')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(
            IterableMatch(*([StrContains()] * (20 + 20 - 1))), -1)
        self.assertFalse(self.mock_cooldown.called)

    async def test_moderator(self):
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(
            IterableMatch(':)',
                          ':) FrankerZ',
                          ':) FrankerZ PogChamp',
                          ':) FrankerZ',
                          ':)'), -1)
        self.mock_cooldown.assert_called_once_with(
            args, timedelta(seconds=30), 'modPyramid')

    async def test_moderator_limit(self):
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        message = Message('!rpyramid 10')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(
            IterableMatch(':)',
                          ':) FrankerZ',
                          ':) FrankerZ PogChamp',
                          ':) FrankerZ PogChamp Kappa',
                          ':) FrankerZ PogChamp Kappa PJSalt',
                          ':) FrankerZ PogChamp Kappa',
                          ':) FrankerZ PogChamp',
                          ':) FrankerZ',
                          ':)'), -1)
        self.mock_cooldown.assert_called_once_with(
            args, timedelta(seconds=30), 'modPyramid')

    async def test_moderator_cooldown(self):
        self.mock_cooldown.return_value = True
        self.permissionSet['moderator'] = True
        self.features.append('modpyramid')
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandRandomPyramid(args), False)
        self.assertFalse(self.channel.send.called)
        self.mock_cooldown.assert_called_once_with(
            args, timedelta(seconds=30), 'modPyramid')

    async def test_limit(self):
        self.mock_config.messageLimit = 30
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(
            IterableMatch(':)',
                          ':) FrankerZ',
                          ':) FrankerZ PogChamp',
                          ':) FrankerZ PogChamp Kappa',
                          ':) FrankerZ PogChamp',
                          ':) FrankerZ',
                          ':)'), -1)
        self.assertFalse(self.mock_cooldown.called)

    async def test_limit_exact(self):
        self.mock_config.messageLimit = 20
        self.permissionSet['broadcaster'] = True
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        message = Message('!rpyramid')
        args = self.args._replace(message=message)
        self.assertIs(await pyramid.commandRandomPyramid(args), True)
        self.channel.send.assert_called_once_with(
            IterableMatch(':)',
                          ':) FrankerZ',
                          ':) FrankerZ PogChamp',
                          ':) FrankerZ',
                          ':)'), -1)
        self.assertFalse(self.mock_cooldown.called)
