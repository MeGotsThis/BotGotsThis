import unittest
from bot.thread.background import BackgroundTasker, Task, run_task
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


def some_task_to_run(now):
    pass


class TestTask(unittest.TestCase):
    def setUp(self):
        self.taskMethod = Mock(spec=some_task_to_run)
        self.task = Task(self.taskMethod, timedelta(minutes=1))

    def test_task_none(self):
        self.assertRaises(TypeError, Task, None, timedelta)

    def test_task_interval_none(self):
        self.assertRaises(TypeError, Task, self.taskMethod, None)

    def test_task_property(self):
        self.assertIs(self.task.task, self.taskMethod)

    def test_interval(self):
        self.assertEqual(self.task.interval, timedelta(minutes=1))

    def test_timestamp(self):
        self.assertEqual(self.task.timestamp, datetime.min)

    def test_timestamp_set(self):
        self.task.timestamp = datetime(2000, 1, 1)
        self.assertEqual(self.task.timestamp, datetime(2000, 1, 1))

    def test_timestamp_set_none(self):
        with self.assertRaises(TypeError):
            self.task.timestamp = None


class TestBackgroundTasker(unittest.TestCase):
    def setUp(self):
        self.taskMethod = Mock(spec=some_task_to_run)
        self.backgroundTasker = BackgroundTasker()

    def test_add_task(self):
        self.backgroundTasker.addTask(self.taskMethod, timedelta(seconds=120))
        self.assertEqual(len(self.backgroundTasker._tasks), 1)
        self.assertIs(self.backgroundTasker._tasks[0].task, self.taskMethod)
        self.assertEqual(self.backgroundTasker._tasks[0].interval,
                         timedelta(seconds=120))
        self.assertEqual(self.backgroundTasker._tasks[0].timestamp,
                         datetime.min)

    @patch('bot.utils.now', autospec=True)
    @patch('bot.thread.background.run_task', autospec=True)
    def test_runTasks(self, mock_run, mock_now):
        now = datetime(2000, 1, 1, 0, 0, 0)
        self.backgroundTasker.addTask(self.taskMethod, timedelta(seconds=60))
        mock_now.return_value = now
        self.backgroundTasker.runTasks()
        mock_run.assert_called_once_with(self.taskMethod, now)
        mock_run.reset_mock()
        mock_now.return_value = now + timedelta(seconds=30)
        self.backgroundTasker.runTasks()
        self.assertFalse(mock_run.called)
        mock_now.return_value = now + timedelta(seconds=60)
        self.backgroundTasker.runTasks()
        mock_run.assert_called_once_with(self.taskMethod,
                                         now + timedelta(seconds=60))


class TestBackgroundRunTask(unittest.TestCase):
    def setUp(self):
        self.taskMethod = Mock(spec=some_task_to_run)
        self.now = datetime(2000, 1, 1, 0, 0, 0)

        patcher = patch('bot.utils.logException')
        self.addCleanup(patcher.stop)
        self.mock_logException = patcher.start()

    def test(self):
        run_task(self.taskMethod, self.now)
        self.taskMethod.assert_called_once_with(self.now)
        self.assertFalse(self.mock_logException.called)

    def test_exception(self):
        self.taskMethod.side_effect = Exception
        run_task(self.taskMethod, self.now)
        self.taskMethod.assert_called_once_with(self.now)
        self.mock_logException.assert_called_once_with()
