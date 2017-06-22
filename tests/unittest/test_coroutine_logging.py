import asynctest

import bot.coroutine.logging

from collections import deque

from asynctest.mock import CoroutineMock, MagicMock, patch


class TestLogging(asynctest.TestCase):
    def setUp(self):
        patcher = patch('bot.coroutine.logging._queue')
        self.addCleanup(patcher.stop)
        patcher.start()
        bot.coroutine.logging._queue = deque()

    @asynctest.fail_on(unused_loop=False)
    def test_log(self):
        bot.coroutine.logging.log('log', 'Kappa')
        self.assertEqual(bot.coroutine.logging._queue[0], ('log', 'Kappa'))

    @patch('aiofiles.open')
    async def test_process_log(self, mockopen):
        file_mock = MagicMock()
        file_mock.__aenter__ = CoroutineMock()
        file_mock.__aenter__.return_value = file_mock
        file_mock.__aexit__ = CoroutineMock()
        file_mock.__aexit__.return_value = True
        mockopen.return_value = file_mock
        bot.coroutine.logging._queue = deque([('log', 'Kappa')])
        await bot.coroutine.logging._process_log()
        self.assertTrue(mockopen.called)
        self.assertTrue(file_mock.write.called)
