from datetime import timedelta
from source.data.message import Message
from source.public.channel import wall
from unittest.mock import ANY, patch
from unittests.public.test_channel import TestChannel


class TestChannelWall(TestChannel):
    def setUp(self):
        super().setUp()
        self.permissions.broadcaster = False
        self.permissions.globalModerator = False
        self.permissions.chatModerator = False

    @patch('source.public.channel.wall.process_wall', autospec=True)
    def test_wall_false(self, mock_process):
        self.assertIs(wall.commandWall(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(wall.commandWall(self.args), False)
        self.assertFalse(mock_process.called)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.wall.process_wall', autospec=True)
    def test_wall(self, mock_process):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        message = Message('!wall Kappa')
        self.assertIs(
            wall.commandWall(self.args._replace(message=message)), True)
        mock_process.assert_called_once_with(
            ANY, 'Kappa Kappa Kappa Kappa Kappa', 20)

    @patch('source.public.channel.wall.process_wall', autospec=True)
    def test_wall_rows(self, mock_process):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        message = Message('!wall Kappa 10')
        self.assertIs(
            wall.commandWall(self.args._replace(message=message)), True)
        mock_process.assert_called_once_with(
            ANY, 'Kappa Kappa Kappa Kappa Kappa', 10)

    @patch('source.public.channel.wall.process_wall', autospec=True)
    def test_wall_repeat_rows(self, mock_process):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        message = Message('!wall Kappa 3 10')
        self.assertIs(
            wall.commandWall(self.args._replace(message=message)), True)
        mock_process.assert_called_once_with(ANY, 'Kappa Kappa Kappa', 10)

    @patch('source.public.channel.wall.process_wall', autospec=True)
    def test_wall_moderator(self, mock_process):
        self.permissionSet['moderator'] = True
        self.features.append('modwall')
        mock_process.return_value = True
        message = Message('!wall Kappa')
        self.assertIs(
            wall.commandWall(self.args._replace(message=message)), True)
        mock_process.assert_called_once_with(ANY, 'Kappa Kappa Kappa', 5)

    @patch('source.public.channel.wall.process_wall', autospec=True)
    def test_long_wall_false(self, mock_process):
        self.assertIs(wall.commandWallLong(self.args), False)
        self.permissionSet['moderator'] = True
        self.assertIs(wall.commandWallLong(self.args), False)
        self.assertFalse(mock_process.called)
        self.assertFalse(self.channel.send.called)

    @patch('source.public.channel.wall.process_wall', autospec=True)
    def test_long_wall(self, mock_process):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        message = Message('!wall- Kappa Kappa')
        self.assertIs(
            wall.commandWallLong(self.args._replace(message=message)),
            True)
        mock_process.assert_called_once_with(ANY, 'Kappa Kappa', 20)

    @patch('source.public.channel.wall.process_wall', autospec=True)
    def test_long_wall_count(self, mock_process):
        self.permissions.broadcaster = True
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        message = Message('!wall-10 Kappa Kappa')
        self.assertIs(
            wall.commandWallLong(self.args._replace(message=message)),
            True)
        mock_process.assert_called_once_with(ANY, 'Kappa Kappa', 10)

    @patch('source.public.channel.wall.process_wall', autospec=True)
    def test_long_wall_moderator(self, mock_process):
        self.permissionSet['moderator'] = True
        self.features.append('modwall')
        mock_process.return_value = True
        message = Message('!wall- Kappa Kappa')
        self.assertIs(
            wall.commandWallLong(self.args._replace(message=message)),
            True)
        mock_process.assert_called_once_with(ANY, 'Kappa Kappa', 5)

    @patch('source.public.channel.wall.config', autospec=True)
    @patch('source.public.channel.wall.inCooldown', autospec=True)
    @patch('source.public.channel.wall.timeout.record_timeout',
           autospec=True)
    def test_process_wall(self, mock_timeout, mock_cooldown, mock_config):
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(wall.process_wall(self.args, 'Kappa', 0), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]), [])

    @patch('source.public.channel.wall.config', autospec=True)
    @patch('source.public.channel.wall.inCooldown', autospec=True)
    @patch('source.public.channel.wall.timeout.record_timeout',
           autospec=True)
    def test_process_wall_1(self, mock_timeout, mock_cooldown, mock_config):
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(wall.process_wall(self.args, 'Kappa', 1), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]), ['Kappa'])

    @patch('source.public.channel.wall.config', autospec=True)
    @patch('source.public.channel.wall.inCooldown', autospec=True)
    @patch('source.public.channel.wall.timeout.record_timeout',
           autospec=True)
    def test_process_wall_2(self, mock_timeout, mock_cooldown, mock_config):
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(wall.process_wall(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(mock_timeout.called)
        self.assertEqual(list(self.channel.send.call_args[0][0]),
                         ['Kappa', 'Kappa \ufeff'])

    @patch('source.public.channel.wall.config', autospec=True)
    @patch('source.public.channel.wall.inCooldown', autospec=True)
    @patch('source.public.channel.wall.timeout.record_timeout',
           autospec=True)
    def test_process_wall_5(self, mock_timeout, mock_cooldown, mock_config):
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.assertIs(wall.process_wall(self.args, 'Kappa', 5), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(mock_timeout.called)
        self.assertEqual(
            list(self.channel.send.call_args[0][0]),
            ['Kappa', 'Kappa \ufeff', 'Kappa', 'Kappa \ufeff', 'Kappa'])

    @patch('source.public.channel.wall.config', autospec=True)
    @patch('source.public.channel.wall.inCooldown', autospec=True)
    @patch('source.public.channel.wall.timeout.record_timeout',
           autospec=True)
    def test_process_wall_channel_mod(self, mock_timeout, mock_cooldown,
                                      mock_config):
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.permissions.globalModerator = True
        self.permissions.chatModerator = True
        self.assertIs(wall.process_wall(self.args, 'Kappa', 2), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        mock_timeout.assert_called_once_with(
            self.database, self.channel, 'botgotsthis', 'Kappa',
            str(self.args.message), 'wall')
        self.assertEqual(list(self.channel.send.call_args[0][0]),
                         ['Kappa', 'Kappa'])

    @patch('source.public.channel.wall.config', autospec=True)
    @patch('source.public.channel.wall.inCooldown', autospec=True)
    @patch('source.public.channel.wall.timeout.record_timeout',
           autospec=True)
    def test_process_wall_broadcaster_limit(
            self, mock_timeout, mock_cooldown, mock_config):
        mock_config.spamModeratorCooldown = 30
        self.permissions.broadcaster = True
        self.assertIs(wall.process_wall(self.args, 'Kappa ', 1000), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_cooldown.called)
        self.assertFalse(mock_timeout.called)
        self.assertEqual(len(list(self.channel.send.call_args[0][0])), 500)

    @patch('source.public.channel.wall.config', autospec=True)
    @patch('source.public.channel.wall.inCooldown', autospec=True)
    @patch('source.public.channel.wall.timeout.record_timeout',
           autospec=True)
    def test_process_wall_moderator_limit(
            self, mock_timeout, mock_cooldown, mock_config):
        mock_config.spamModeratorCooldown = 30
        mock_cooldown.return_value = False
        self.assertIs(wall.process_wall(self.args, 'Kappa', 100), True)
        self.channel.send.assert_called_once_with(ANY, -1)
        self.assertFalse(mock_timeout.called)
        mock_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), ANY)
        self.assertEqual(len(list(self.channel.send.call_args[0][0])), 10)

    @patch('source.public.channel.wall.config', autospec=True)
    @patch('source.public.channel.wall.inCooldown', autospec=True)
    @patch('source.public.channel.wall.timeout.record_timeout',
           autospec=True)
    def test_process_wall_moderator_cooldown(
            self, mock_timeout, mock_cooldown, mock_config):
        mock_config.spamModeratorCooldown = 30
        mock_cooldown.return_value = True
        self.assertIs(wall.process_wall(self.args, 'Kappa', 2), False)
        self.assertFalse(self.channel.send.called)
        self.assertFalse(mock_timeout.called)
        mock_cooldown.assert_called_once_with(
            self.args, timedelta(seconds=30), ANY)