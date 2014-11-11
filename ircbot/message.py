# Message Queue
from config import config
import ircbot.irc
import threading
import traceback
import datetime
import time
import sys

class MessgeQueue(threading.Thread):
    def __init__(self, *args):
        threading.Thread.__init__(self, *args)
        self.queues = [[], [], []]
        self.lowQueueRecent = []
        self.queue = []
        self.timesSent = []
        self.publicTime = datetime.datetime.min
        self.lock = threading.Lock()
        self.running = True
    
    def queueMessage(self, channelThread, message, priority):
        self.lock.acquire()
        self.queues[priority].append((channelThread, message))
        self.lock.release()
    
    def run(self):
        print('Starting MessageQueue')
        try:
            while self.running:
                msg = self._getMessage()
                if msg is not None:
                    if config.botnick not in msg[0].mods:
                        self.publicTime = datetime.datetime.utcnow()
                    self.timesSent.append(datetime.datetime.utcnow())
                    _ = 'PRIVMSG ' + msg[0].channel + ' :' + msg[1] + '\n'
                    msg[0].sendIrcCommand(_)
                time.sleep(1/20)
        except Exception as e:
            now = datetime.datetime.now()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            _ = traceback.format_exception(exc_type, exc_value, exc_traceback)
            if config.exceptionLog is not None:
                with open(config.exceptionLog, 'a') as file:
                    file.write(now.strftime('%Y-%m-%d %H:%M:%S.%f '))
                    file.write(' ' + ''.join(_))
            raise
        finally:
            print('Ending MessageQueue')
    
    def _getMessage(self):
        msgDuration = datetime.timedelta(seconds=30.1)
        publicDelay = datetime.timedelta(seconds=config.publicDelay)
        botnick = config.botnick
        self.timesSent = [t for t in self.timesSent
                          if datetime.datetime.utcnow() - t <= msgDuration]
        isModGood = len(self.timesSent) < config.modLimit
        isModSpamGood = len(self.timesSent) < config.modSpamLimit
        _ = self.publicTime + publicDelay <= datetime.datetime.utcnow()
        isPublicGood = _ and len(self.timesSent) < config.publicLimit
        
        msg = None
        self.lock.acquire()
        if isPublicGood:
            for j in [0, 1]:
                if msg is None:
                    queue = self.queues[j]
                    for i in range(len(queue)):
                        if botnick not in queue[i][0].mods:
                            msg = queue[i]
                            del queue[i]
                            break
            if msg is None:
                queue = self.queues[2]
                for i in range(len(queue)):
                    if botnick not in queue[i][0].mods:
                        msg = queue[i]
                        del queue[i]
                        break
        if isModGood:
            for j in [0, 1]:
                if msg is None:
                    queue = self.queues[j]
                    for i in range(len(queue)):
                        if botnick in queue[i][0].mods:
                            msg = queue[i]
                            del queue[i]
                            break
            if msg is None:
                queue = self.queues[2]
                for i in range(len(queue)):
                    if (queue[i][0].channel not in self.lowQueueRecent and
                        botnick in queue[i][0].mods):
                        msg = queue[i]
                        del queue[i]
                        self.lowQueueRecent.append(msg[0].channel)
                        break
        if isModSpamGood:
            if msg is None:
                queue = self.queues[2]
                for channel in self.lowQueueRecent:
                    for i in range(len(queue)):
                        if (queue[i][0].channel == channel and
                            botnick in queue[i][0].mods):
                            msg = queue[i]
                            del queue[i]
                            self.lowQueueRecent.remove(msg[0].channel)
                            self.lowQueueRecent.append(msg[0].channel)
                            break
                    if msg is not None:
                        break
            if msg is None:
                if len(self.queues[2]) == 0:
                    self.lowQueueRecent.clear()
        self.lock.release()
        return msg
    
    def clearQueue(self, channel):
        self.lock.acquire()
        for j in [0, 1, 2]:
            queue = self.queues[j]
            for msg in queue[:]:
                if msg[1] == channel:
                    queue.remove(msg)
        self.lock.release()
    
    def clearAllQueue(self):
        self.lock.acquire()
        for j in [0, 1, 2]:
            self.queues[j].clear()
        self.lock.release()
