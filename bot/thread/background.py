from .. import globals, utils
from datetime import datetime, timedelta
from typing import Callable, List
import threading
import time


class BackgroundTasker(threading.Thread):
    def __init__(self, **kwargs) -> None:
        threading.Thread.__init__(self, **kwargs)
        self._tasks = []  # type: List[Task]
    
    def run(self) -> None:
        print('{time} Starting {name}'.format(
            time=datetime.utcnow(), name=self.__class__.__name__))
        try:
            while globals.running:
                self.runTasks()
                time.sleep(1 / 1000)
        except:
            utils.logException()
            raise
        finally:
            print('{time} Ending {name}'.format(
                time=datetime.utcnow(), name=self.__class__.__name__))
    
    def addTask(self, task, interval=timedelta(seconds=60)) -> None:
        self._tasks.append(Task(task, interval))
    
    def runTasks(self) -> None:
        timestamp = datetime.utcnow()  # type: datetime
        for task in self._tasks:  # --type: Task
            if timestamp >= task.timestamp + task.interval:
                threading.Thread(
                    target=task.task, args=(timestamp,)).start()
                task.timestamp = timestamp


class Task:
    def __init__(self,
                 task:Callable[[datetime], None],
                 interval:timedelta) -> None:
        self._task = task
        self._interval = interval
        self.timestamp = datetime.min  # type: datetime

    @property
    def task(self) -> Callable[[datetime], None]:
        return self._task
    
    @property
    def interval(self) -> timedelta:
        return self._interval
