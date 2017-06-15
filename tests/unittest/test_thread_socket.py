import unittest
from bot.data import SocketHandler
from bot.thread.socket import SocketsThread
from unittest.mock import Mock, PropertyMock, patch


class TestSocketThread(unittest.TestCase):
    def setUp(self):
        self.socketThead = SocketsThread()

        self.socket1 = Mock(spec=SocketHandler)
        self.socket1_isConnected = PropertyMock(return_value=True)
        type(self.socket1).isConnected = self.socket1_isConnected

        self.socket2 = Mock(spec=SocketHandler)
        self.socket2_isConnected = PropertyMock(return_value=False)
        type(self.socket2).isConnected = self.socket2_isConnected
        self.socket2.disconnect.side_effect = ConnectionError

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.clusters = {'1': self.socket1, '2': self.socket2}

    @patch('select.select')
    def test_process_connect(self, mock_select):
        mock_select.return_value = [], [], []
        self.socketThead.process()
        self.socket2.connect.assert_called_once_with()
        self.socket1.queueMessages.assert_called_once_with()
        self.socket1.sendPing.assert_called_once_with()
        self.assertFalse(self.socket1.read.called)
        self.assertFalse(self.socket1.flushWrite.called)

    @patch('select.select')
    def test_process_read(self, mock_select):
        mock_select.return_value = [self.socket1], [], []
        self.socketThead.process()
        self.socket1.read.assert_called_once_with()
        self.assertFalse(self.socket1.flushWrite.called)

    @patch('select.select')
    def test_process_write(self, mock_select):
        mock_select.return_value = [], [self.socket1], []
        self.socketThead.process()
        self.socket1.flushWrite.assert_called_once_with()
        self.assertFalse(self.socket1.read.called)

    @patch('select.select')
    def test_process_read_write(self, mock_select):
        mock_select.return_value = [self.socket1], [self.socket1], []
        self.socketThead.process()
        self.socket1.read.assert_called_once_with()
        self.socket1.flushWrite.assert_called_once_with()
        self.socket1.sendPing.assert_called_once_with()

    @patch('select.select')
    def test_process_read_reset_write(self, mock_select):
        mock_select.return_value = [self.socket1], [self.socket1], []
        def changeConnection():
            self.socket1_isConnected.return_value = False
        self.socket1.read = changeConnection
        self.socketThead.process()
        self.assertFalse(self.socket1.flushWrite.called)
        self.assertFalse(self.socket1.sendPing.called)

    @patch('select.select')
    def test_process_reset_read_write(self, mock_select):
        mock_select.return_value = [self.socket1], [self.socket1], []
        self.socket1_isConnected.side_effect = [True, True, True, False, False, False]
        self.socketThead.process()
        self.assertFalse(self.socket1.read.called)
        self.assertFalse(self.socket1.flushWrite.called)
        self.assertFalse(self.socket1.sendPing.called)

    def test_terminate(self):
        self.socketThead.terminate()
        self.socket1.disconnect.assert_called_once_with()
        self.socket2.disconnect.assert_called_once_with()
