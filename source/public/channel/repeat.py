import threading
import time
from contextlib import suppress
from datetime import datetime, timedelta
from ..library import timeout
from ..library.chat import permission
from ...database.factory import getDatabase


@permission('broadcaster')
def commandAutoRepeat(args):
    """
    !autorepeat 1 MONEY MONEY
    !autorepeat 0
    !autorepeat off
    """
    
    count = None
    return processAutoRepeat(args, count)

@permission('broadcaster')
def commandAutoRepeatCount(args):
    """
    !autorepeat-20 0.5 MONEY MONEY 
    !autorepeat-20 0
    !autorepeat-20 off
    """
    
    count = 10
    with suppress(ValueError, IndexError):
        count = int(args.message.command.split('autorepeat-')[1])
    return processAutoRepeat(args, count)

def processAutoRepeat(args, count):
    try:
        if args.message.lower[1] == 'off':
            minutesDuration = 0
        else:
            minutesDuration = float(args.message[1])
    except (ValueError, IndexError):
        return False
    
    message = args.message[2:] or None
    if 'repeatThread' in args.chat.sessionData:
        args.chat.sessionData['repeatThread'].count = 0
    
    if minutesDuration <= 0 or count == 0 or not message:
        return True
    
    thread = MessageRepeater(
        chat=args.chat, message=message,
        duration=timedelta(minutes=minutesDuration), count=count)
    args.chat.sessionData['repeatThread'] = thread
    thread.start()
    return True

class MessageRepeater(threading.Thread):
    def __init__(self, *args,
                 chat, message='', duration=timedelta(), count=None):
        threading.Thread.__init__(self, *args)
        self._chat = chat
        self._message = message
        self._count = count
        self._duration = max(duration, timedelta(seconds=1))
        self._lastTime = datetime.min
        self._countLock = threading.Lock()
    
    @property
    def count(self):
        with self._countLock:
            return self._count
    
    @count.setter
    def count(self, value):
        with self._countLock:
            self._count = value
    
    def run(self):
        while self._continueRunning():
            self.process()
            time.sleep(1/20)
        if ('repeatThread' in self._chat.sessionData
            and self._chat.sessionData['repeatThread'] is self):
            del self._chat.sessionData['repeatThread']
    
    def process(self):
        if datetime.utcnow() >= self._lastTime + self._duration:
            self._lastTime = datetime.utcnow()
            self._chat.send(self._message)
            if self._chat.isMod:
                with getDatabase() as database:
                    timeout.recordTimeoutFromCommand(
                        database, self._chat, None, self._message, None,
                        'autorepeat')
            with self._countLock:
                if self._count is not None:
                    self._count -= 1
    
    def _continueRunning(self):
        with self._countLock:
            return self._count is None or self._count > 0
    
