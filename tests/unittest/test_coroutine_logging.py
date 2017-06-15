import asynctest

import bot.coroutine.logging

from collections import deque

from asynctest.mock import mock_open, patch


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

    @patch('aiofiles.open', new_callable=mock_open)
    async def fail_test_runTasks(self, mockopen):
        # TODO: Fix when asynctest is updated with magic mock
        bot.coroutine.logging._queue = deque([('log', 'Kappa')])
        await bot.coroutine.logging._process_log()
        self.assertTrue(mockopen.called)
        self.assertTrue(mockopen().write.called)
