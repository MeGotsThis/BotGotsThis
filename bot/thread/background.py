from .. import globals, utils
from datetime import datetime, timedelta
import threading
import time


class BackgroundTasker(threading.Thread):
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
        self._tasks = []
    
    def run(self):
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
    
    def addTask(self, task, interval=timedelta(seconds=60)):
        self._tasks.append(Task(task, interval))
    
    def runTasks(self):
        timestamp = datetime.utcnow()
        for task in self._tasks:
            if timestamp >= task.timestamp + task.interval:
                threading.Thread(
                    target=task.task, args=(timestamp,)).start()
                task.timestamp = timestamp

class Task:
    def __init__(self, task, interval):
        self._task = task
        self._interval = interval
        self.timestamp = datetime.min

    @property
    def task(self):
        return self._task
    
    @property
    def interval(self):
        return self._interval
