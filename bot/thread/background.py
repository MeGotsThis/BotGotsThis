from .. import utils
from datetime import datetime, timedelta
from typing import Callable, List
import bot.globals
import threading
import time


class BackgroundTasker(threading.Thread):
    def __init__(self, **kwargs) -> None:
        threading.Thread.__init__(self, **kwargs)  # type: ignore
        self._tasks = []  # type: List[Task]
    
    def run(self) -> None:
        print('{time} Starting {name}'.format(
            time=utils.now(), name=self.__class__.__name__))
        try:
            while bot.globals.running:
                self.runTasks()
                time.sleep(1 / 1000)
        except:
            utils.logException()
            raise
        finally:
            print('{time} Ending {name}'.format(
                time=utils.now(), name=self.__class__.__name__))
    
    def addTask(self,
                task: Callable[[datetime], None],
                interval: timedelta=timedelta(seconds=60)) -> None:
        self._tasks.append(Task(task, interval))
    
    def runTasks(self) -> None:
        timestamp = utils.now()  # type: datetime
        for task in self._tasks[:]:  # type: Task
            if timestamp >= task.timestamp + task.interval:
                threading.Thread(
                    target=run_task, args=(task.task, timestamp,)).start()
                task.timestamp = timestamp


def run_task(task: Callable[[datetime], None],
             timestamp: datetime) -> None:
    try:
        task(timestamp)
    except:
        utils.logException()


class Task:
    def __init__(self,
                 task: Callable[[datetime], None],
                 interval: timedelta) -> None:
        # TODO: mypy fix
        if not isinstance(task, Callable):  # type: ignore
            raise TypeError()
        if not isinstance(interval, timedelta):
            raise TypeError()
        self._task = task
        self._interval = interval
        self._timestamp = datetime.min  # type: datetime

    @property
    def task(self) -> Callable[[datetime], None]:
        return self._task
    
    @property
    def interval(self) -> timedelta:
        return self._interval

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError()
        self._timestamp = value
