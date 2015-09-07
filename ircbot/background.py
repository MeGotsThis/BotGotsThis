import datetime
import ircbot.irc
import threading
import time

_tasks = []

class BackgroundTasker(threading.Thread):
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
        self._running = True
    
    @property
    def running(self):
        return self._running
    
    @running.setter
    def running(self, value):
        self._running = value
    
    def run(self):
        print(str(datetime.datetime.utcnow()) + ' Starting BackgroundTasker')
        try:
            while self.running:
                now = datetime.datetime.utcnow()
                for t in _tasks:
                    task, interval, last = t
                    if now >= last + interval:
                        threading.Thread(target=task, args=(now,)).run()
                        t[2] = now
                time.sleep(1 / 1000)
        except:
            ircbot.irc.logException()
            raise
        finally:
            print(str(datetime.datetime.utcnow()) + ' Ending BackgroundTasker')

def addTask(task, interval=datetime.timedelta(seconds=60)):
    t = [task, interval, datetime.datetime.min]
    _tasks.append(t)
