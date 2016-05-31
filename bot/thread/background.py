from .. import globals, utils
import datetime
import threading
import time


class BackgroundTasker(threading.Thread):
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
        self._tasks = []
    
    def run(self):
        print('{time} Starting {name}'.format(
            time=datetime.datetime.utcnow(), name=self.__class__.__name__))
        now = datetime.datetime.utcnow()
        try:
            while globals.running:
                now = datetime.datetime.utcnow()
                for t in self._tasks:
                    task, interval, last = t
                    if now >= last + interval:
                        threading.Thread(target=task, args=(now,)).start()
                        t[2] = now
                time.sleep(1 / 1000)
        except:
            utils.logException(None, now)
            raise
        finally:
            print('{time} Ending {name}'.format(
                time=datetime.datetime.utcnow(), name=self.__class__.__name__))
    
    def addTask(self, task, interval=datetime.timedelta(seconds=60)):
        t = [task, interval, datetime.datetime.min]
        self._tasks.append(t)
