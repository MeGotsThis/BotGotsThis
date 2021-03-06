from asynctest.mock import call, patch

from tests.unittest.base_channel import TestChannel
from lib.data.message import Message
from lib.data import AutoRepeatList
from tests.unittest.mock_class import AsyncIterator, StrContains

# Needs to be imported last
from .. import channel


class TestRepeatChannel(TestChannel):
    @patch(channel.__name__ + '.process_auto_repeat')
    async def test_auto_repeat(self, mock_process):
        self.assertIs(await channel.commandAutoRepeat(self.args), False)
        self.assertFalse(mock_process.called)
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        self.assertIs(await channel.commandAutoRepeat(self.args), True)
        mock_process.assert_called_once_with(self.args, None)

    @patch(channel.__name__ + '.process_auto_repeat')
    async def test_auto_repeat_count(self, mock_process):
        self.assertIs(await channel.commandAutoRepeatCount(self.args), False)
        self.assertFalse(mock_process.called)
        self.permissionSet['broadcaster'] = True
        mock_process.return_value = True
        self.assertIs(await channel.commandAutoRepeat(self.args), True)
        mock_process.assert_called_once_with(self.args, None)

    async def test_process_false(self):
        self.assertIs(await channel.process_auto_repeat(self.args, None),
                      False)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process_error(self):
        self.args = self.args._replace(message=Message('!autorepeat abc'))
        self.assertIs(await channel.process_auto_repeat(self.args, None),
                      False)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process_off(self):
        self.args = self.args._replace(message=Message('!autorepeat off abc'))
        self.assertIs(await channel.process_auto_repeat(self.args, None), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.data.removeAutoRepeat.assert_called_once_with(
            self.channel.channel, '')
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process_zero_minutes(self):
        self.args = self.args._replace(message=Message('!autorepeat 0 abc'))
        self.assertIs(await channel.process_auto_repeat(self.args, None), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.data.removeAutoRepeat.assert_called_once_with(
            self.channel.channel, '')
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process_zero_count(self):
        self.args = self.args._replace(message=Message('!autorepeat 1 abc'))
        self.assertIs(await channel.process_auto_repeat(self.args, 0), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.data.removeAutoRepeat.assert_called_once_with(
            self.channel.channel, '')
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process_no_message(self):
        self.args = self.args._replace(message=Message('!autorepeat 1'))
        self.assertIs(await channel.process_auto_repeat(self.args, None), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.data.removeAutoRepeat.assert_called_once_with(
            self.channel.channel, '')
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process(self):
        self.args = self.args._replace(message=Message('!autorepeat 1 Kappa'))
        self.assertIs(await channel.process_auto_repeat(self.args, None), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.data.setAutoRepeat.assert_called_once_with(
            self.channel.channel, '', 'Kappa', None, 1)
        self.assertFalse(self.channel.send.called)

    async def test_process_count(self):
        self.args = self.args._replace(message=Message('!autorepeat 1 Kappa'))
        self.assertIs(await channel.process_auto_repeat(self.args, 1), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.data.setAutoRepeat.assert_called_once_with(
            self.channel.channel, '', 'Kappa', 1, 1)
        self.assertFalse(self.channel.send.called)

    async def test_process_clear(self):
        self.args = self.args._replace(message=Message('!autorepeat clear'))
        self.assertIs(await channel.process_auto_repeat(self.args, 1), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.data.clearAutoRepeat.aasert_called_once_with(
            self.channel.channel)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process_list(self):
        self.args = self.args._replace(message=Message('!autorepeat list'))
        self.data.listAutoRepeat.return_value = AsyncIterator([
            AutoRepeatList('Kappa', 'Keepo', None, 1, self.now),
            AutoRepeatList(':)', ':(', None, 5, self.now),
            ])
        self.assertIs(await channel.process_auto_repeat(self.args, 1), True)
        self.data.listAutoRepeat.assert_called_once_with(
            self.channel.channel)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.assertFalse(self.data.setAutoRepeat.called)
        self.channel.send.assert_has_calls([
            call(StrContains('Auto Repeats')),
            call(StrContains('Kappa', 'Keepo', '1')),
            call(StrContains(':)', ':(', '5')),
            ])

    async def test_process_list_empty(self):
        self.args = self.args._replace(message=Message('!autorepeat list'))
        self.data.listAutoRepeat.return_value = AsyncIterator([])
        self.assertIs(await channel.process_auto_repeat(self.args, 1), True)
        self.data.listAutoRepeat.assert_called_once_with(
            self.channel.channel)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.assertFalse(self.data.setAutoRepeat.called)
        self.channel.send.assert_called_once_with(
            StrContains('No', 'Auto Repeats'))

    async def test_process_name_error(self):
        self.args = self.args._replace(
            message=Message('!autorepeat name=kappa abc'))
        self.assertIs(await channel.process_auto_repeat(self.args, None),
                      False)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process_name_off(self):
        self.args = self.args._replace(
            message=Message('!autorepeat name=kappa off abc'))
        self.assertIs(await channel.process_auto_repeat(self.args, None), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.data.removeAutoRepeat.assert_called_once_with(
            self.channel.channel, 'kappa')
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process_name_zero_minutes(self):
        self.args = self.args._replace(
            message=Message('!autorepeat name=kappa 0 abc'))
        self.assertIs(await channel.process_auto_repeat(self.args, None), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.data.removeAutoRepeat.assert_called_once_with(
            self.channel.channel, 'kappa')
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process_name_zero_count(self):
        self.args = self.args._replace(
            message=Message('!autorepeat name=kappa 1 abc'))
        self.assertIs(await channel.process_auto_repeat(self.args, 0), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.data.removeAutoRepeat.assert_called_once_with(
            self.channel.channel, 'kappa')
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process_name_no_message(self):
        self.args = self.args._replace(
            message=Message('!autorepeat name=kappa 1'))
        self.assertIs(await channel.process_auto_repeat(self.args, None), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.data.removeAutoRepeat.assert_called_once_with(
            self.channel.channel, 'kappa')
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process_name(self):
        self.args = self.args._replace(
            message=Message('!autorepeat name=kappa 1 Kappa'))
        self.assertIs(await channel.process_auto_repeat(self.args, None), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.data.setAutoRepeat.assert_called_once_with(
            self.channel.channel, 'kappa', 'Kappa', None, 1)
        self.assertFalse(self.channel.send.called)

    async def test_process_name_caps(self):
        self.args = self.args._replace(
            message=Message('!autorepeat name=KAPPA 1 Kappa'))
        self.assertIs(await channel.process_auto_repeat(self.args, None), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.data.setAutoRepeat.assert_called_once_with(
            self.channel.channel, 'kappa', 'Kappa', None, 1)
        self.assertFalse(self.channel.send.called)

    async def test_process_name_count(self):
        self.args = self.args._replace(
            message=Message('!autorepeat name=kappa 1 Kappa'))
        self.assertIs(await channel.process_auto_repeat(self.args, 1), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.assertFalse(self.data.clearAutoRepeat.called)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.data.setAutoRepeat.assert_called_once_with(
            self.channel.channel, 'kappa', 'Kappa', 1, 1)
        self.assertFalse(self.channel.send.called)

    async def test_process_name_clear(self):
        self.args = self.args._replace(
            message=Message('!autorepeat name=kappa clear'))
        self.assertIs(await channel.process_auto_repeat(self.args, 1), True)
        self.assertFalse(self.data.listAutoRepeat.called)
        self.data.clearAutoRepeat.aasert_called_once_with(
            self.channel.channel)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.assertFalse(self.data.setAutoRepeat.called)
        self.assertFalse(self.channel.send.called)

    async def test_process_name_list(self):
        self.args = self.args._replace(
            message=Message('!autorepeat name=kappa list'))
        self.data.listAutoRepeat.return_value = AsyncIterator([
            AutoRepeatList('Kappa', 'Keepo', None, 1, self.now),
            AutoRepeatList(':)', ':(', None, 5, self.now),
            ])
        self.assertIs(await channel.process_auto_repeat(self.args, 1), True)
        self.data.listAutoRepeat.assert_called_once_with(
            self.channel.channel)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.assertFalse(self.data.setAutoRepeat.called)
        self.channel.send.assert_has_calls([
            call(StrContains('Auto Repeats')),
            call(StrContains('Kappa', 'Keepo', '1')),
            call(StrContains(':)', ':(', '5')),
            ])

    async def test_process_name_list_empty(self):
        self.args = self.args._replace(
            message=Message('!autorepeat name=kappa list'))
        self.data.listAutoRepeat.return_value = AsyncIterator([])
        self.assertIs(await channel.process_auto_repeat(self.args, 1), True)
        self.data.listAutoRepeat.assert_called_once_with(
            self.channel.channel)
        self.assertFalse(self.data.removeAutoRepeat.called)
        self.assertFalse(self.data.setAutoRepeat.called)
        self.channel.send.assert_called_once_with(
            StrContains('No', 'Auto Repeats'))
