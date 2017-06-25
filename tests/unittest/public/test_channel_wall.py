from datetime import timedelta

from asynctest.mock import patch

from source.data.message import Message
from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import IterableMatch, StrContains

# Needs to be imported last
from source.public.channel import wall


class TestChannelWall(TestChannel):
    def setUp(self):
        super().setUp()
        self.permissions.broadcaster = False
        self.permissions.globalModerator = False
        self.permissions.chatModerator = False

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.messageLimit = 100

        patcher = patch('source.public.channel.wall.process_wall')
        self.addCleanup(patcher.stop)
        self.mock_process = patcher.start()

    async def test_wall_false(self):
        self.assertIs(await wall.commandWall(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(await wall.commandWall(self.args), False)
        self.assertFalse(self.mock_process.called)
        self.assertFalse(self.channel.send.called)

    async def test_wall(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!wall Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await wall.commandWall(args), True)
        self.mock_process.assert_called_once_with(
            args, 'Kappa Kappa Kappa Kappa Kappa', 20)

    async def test_wall_rows(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!wall Kappa 10')
        args = self.args._replace(message=message)
        self.assertIs(await wall.commandWall(args), True)
        self.mock_process.assert_called_once_with(
            args, 'Kappa Kappa Kappa Kappa Kappa', 10)

    async def test_wall_repeat_rows(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!wall Kappa 3 10')
        args = self.args._replace(message=message)
        self.assertIs(await wall.commandWall(args), True)
        self.mock_process.assert_called_once_with(
            args, 'Kappa Kappa Kappa', 10)

    async def test_wall_repeat_rows_limit(self):
        self.mock_config.messageLimit = 25
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!wall Kappa 10 10')
        args = self.args._replace(message=message)
        self.assertIs(await wall.commandWall(args), True)
        self.mock_process.assert_called_once_with(
            args, 'Kappa Kappa Kappa Kappa', 10)

    async def test_wall_repeat_rows_limit_exact(self):
        self.mock_config.messageLimit = 29
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!wall Kappa 10 10')
        args = self.args._replace(message=message)
        self.assertIs(await wall.commandWall(args), True)
        self.mock_process.assert_called_once_with(
            args, 'Kappa Kappa Kappa Kappa Kappa', 10)

    async def test_wall_moderator(self):
        self.permissionSet['moderator'] = True
        self.features.append('modwall')
        self.mock_process.return_value = True
        message = Message('!wall Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await wall.commandWall(args), True)
        self.mock_process.assert_called_once_with(args, 'Kappa Kappa Kappa', 5)

    async def test_long_wall_false(self):
        self.assertIs(await wall.commandWallLong(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(await wall.commandWallLong(self.args), False)
        self.assertFalse(self.mock_process.called)
        self.assertFalse(self.channel.send.called)

    async def test_long_wall(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!wall- Kappa Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await wall.commandWallLong(args), True)
        self.mock_process.assert_called_once_with(args, 'Kappa Kappa', 20)

    async def test_long_wall_count(self):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        self.mock_process.return_value = True
        message = Message('!wall-10 Kappa Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await wall.commandWallLong(args), True)
        self.mock_process.assert_called_once_with(args, 'Kappa Kappa', 10)

    async def test_long_wall_moderator(self):
        self.permissionSet['moderator'] = True
        self.features.append('modwall')
        self.mock_process.return_value = True
        message = Message('!wall- Kappa Kappa')
        args = self.args._replace(message=message)
        self.assertIs(await wall.commandWallLong(args), True)
        self.mock_process.assert_called_once_with(args, 'Kappa Kappa', 5)


class TestChannelWallProcess(TestChannel):
    def setUp(self):
        super().setUp()
        self.permissions.broadcaster = False
        self.permissions.globalModerator = False
        self.permissions.chatModerator = False

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
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
        self.assertIs(await wall.process_wall(self.args, 'Kappa', 0), True)
        self.channel.send.assert_called_once_with(IterableMatch(), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_1(self):
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(await wall.process_wall(self.args, 'Kappa', 1), True)
        self.channel.send.assert_called_once_with(IterableMatch('Kappa'), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_2(self):
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(await wall.process_wall(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(
            IterableMatch('Kappa', 'Kappa \ufeff'), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_5(self):
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(await wall.process_wall(self.args, 'Kappa', 5), True)
        self.channel.send.assert_called_once_with(
            IterableMatch('Kappa', 'Kappa \ufeff', 'Kappa', 'Kappa \ufeff',
                          'Kappa'),
            -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_channel_mod(self):
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.permissions.chatModerator = True
        self.assertIs(await wall.process_wall(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(
            IterableMatch('Kappa', 'Kappa'), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.mock_timeout.assert_called_once_with(
            self.channel, 'botgotsthis', 'Kappa',
            str(self.args.message), 'wall')

    async def test_broadcaster_limit(self):
        self.permissions.broadcaster = True
        self.assertIs(await wall.process_wall(self.args, 'Kappa ', 1000), True)
        self.channel.send.assert_called_once_with(
            IterableMatch(*([StrContains()] * (500))), -1)
        self.assertFalse(self.mock_cooldown.called)
        self.assertFalse(self.mock_timeout.called)

    async def test_moderator_limit(self):
        self.mock_cooldown.return_value = False
        self.assertIs(await wall.process_wall(self.args, 'Kappa', 100), True)
        self.channel.send.assert_called_once_with(
            IterableMatch(*([StrContains()] * (10))), -1)
        self.assertFalse(self.mock_timeout.called)
        self.mock_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), 'modWall')

    async def test_moderator_cooldown(self):
        self.mock_cooldown.return_value = True
        self.assertIs(await wall.process_wall(self.args, 'Kappa', 2), False)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(self.mock_timeout.called)
        self.mock_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), 'modWall')
