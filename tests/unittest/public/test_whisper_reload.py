from asynctest.mock import patch

import bot.utils
from tests.unittest.base_whisper import TestWhisper
from tests.unittest.mock_class import PartialMatch

# Needs to be imported last
from source.public.whisper import reload


class TestWhisperReload(TestWhisper):
    @patch('source.public.library.reload.full_reload', autospec=True)
    async def test_reload(self, mock_reload):
        self.assertIs(await reload.commandReload(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissionSet['owner'] = True
        self.assertIs(await reload.commandReload(self.args), True)
        mock_reload.assert_called_once_with(
            PartialMatch(bot.utils.whisper, 'botgotsthis'))

    @patch('source.public.library.reload.reload_commands', autospec=True)
    async def test_reload_commands(self, mock_reload):
        self.assertIs(await reload.commandReloadCommands(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissionSet['manager'] = True
        self.assertIs(await reload.commandReloadCommands(self.args), True)
        mock_reload.assert_called_once_with(
            PartialMatch(bot.utils.whisper, 'botgotsthis'))

    @patch('source.public.library.reload.reload_config', autospec=True)
    async def test_reload_config(self, mock_reload):
        self.assertIs(await reload.commandReloadConfig(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissionSet['owner'] = True
        self.assertIs(await reload.commandReloadConfig(self.args), True)
        mock_reload.assert_called_once_with(
            PartialMatch(bot.utils.whisper, 'botgotsthis'))
