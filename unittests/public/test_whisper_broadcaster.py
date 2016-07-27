from source.public.whisper import broadcaster
from unittest.mock import ANY, patch
from unittests.public.test_whisper import TestWhisper


class TestWhisperBroadcaster(TestWhisper):
    @patch('source.public.whisper.broadcaster.broadcaster.come', autospec=True)
    def test_come(self, mock_come):
        mock_come.return_value = True
        self.assertIs(broadcaster.commandCome(self.args), True)
        mock_come.assert_called_once_with(self.database, 'botgotsthis', ANY)

    @patch('source.public.whisper.broadcaster.broadcaster.leave', autospec=True)
    def test_leave(self, mock_leave):
        mock_leave.return_value = True
        self.assertIs(broadcaster.commandLeave(self.args), True)
        mock_leave.assert_called_once_with('botgotsthis', ANY)

    @patch('source.public.whisper.broadcaster.broadcaster.empty', autospec=True)
    def test_empty(self, mock_empty):
        mock_empty.return_value = True
        self.assertIs(broadcaster.commandEmpty(self.args), True)
        mock_empty.assert_called_once_with('botgotsthis', ANY)

    @patch('source.public.whisper.broadcaster.broadcaster.auto_join',
           autospec=True)
    def test_auto_join(self, mock_autojoin):
        mock_autojoin.return_value = True
        self.assertIs(broadcaster.commandAutoJoin(self.args), True)
        mock_autojoin.assert_called_once_with(self.database, 'botgotsthis',
                                              ANY, self.args.message)
