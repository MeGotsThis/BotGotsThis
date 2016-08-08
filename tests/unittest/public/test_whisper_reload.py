from unittest.mock import ANY, patch

from source.public.whisper import reload
from tests.unittest.base_whisper import TestWhisper


class TestWhisperReload(TestWhisper):
    @patch('source.public.library.reload.full_reload', autospec=True)
    def test_reload(self, mock_reload):
        self.assertIs(reload.commandReload(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissionSet['owner'] = True
        self.assertIs(reload.commandReload(self.args), True)
        mock_reload.assert_called_once_with(ANY)

    @patch('source.public.library.reload.reload_commands', autospec=True)
    def test_reload_commands(self, mock_reload):
        self.assertIs(reload.commandReloadCommands(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissionSet['owner'] = True
        self.assertIs(reload.commandReloadCommands(self.args), True)
        mock_reload.assert_called_once_with(ANY)

    @patch('source.public.library.reload.reload_config', autospec=True)
    def test_reload_config(self, mock_reload):
        self.assertIs(reload.commandReloadConfig(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissionSet['owner'] = True
        self.assertIs(reload.commandReloadConfig(self.args), True)
        mock_reload.assert_called_once_with(ANY)
