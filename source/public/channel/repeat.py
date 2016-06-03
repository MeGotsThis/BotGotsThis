from ...database.factory import getDatabase
from ..library import timeout
from ..library.chat import permission
import threading
import datetime
import time
import json

@permission('broadcaster')
def commandAutoRepeat(args):
    """
    !autorepeat 1 MONEY MONEY
    !autorepeat-20 0.5 MONEY MONEY 
    !autorepeat-20 0
    !autorepeat-20 off
    """

    if 'autorepeat-' in args.message.command:
        try:
            count = int(args.message.command.split('autorepeat-')[1])
        except:
            count = 10
    else:
        count = None
    try:
        if args.message.lower[1] == 'off':
            minutesDuration = 0
        else:
            minutesDuration = float(args.message[1])
    except:
        return False
    
    try:
        messageToSend = args.message[2:]
    except IndexError:
        messageToSend = None
    
    if 'repeatThread' in args.chat.sessionData:
        args.chat.sessionData['repeatThread'].count = 0
    
    if minutesDuration <= 0 or count == 0 or not messageToSend:
        return True
    
    thread = MessageRepeater(
        chat=args.chat,
        message=messageToSend,
        duration=datetime.timedelta(minutes=minutesDuration),
        count=count)
    args.chat.sessionData['repeatThread'] = thread
    thread.start()
    
    return True

class MessageRepeater(threading.Thread):
    def __init__(self, *args,
                 chat, message='', duration=datetime.timedelta(), count=None):
        threading.Thread.__init__(self, *args)
        self._chat = chat
        self._message = message
        self._count = count
        self._duration = max(duration, datetime.timedelta(seconds=1))
        self._lastTime = datetime.datetime.min
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
            if datetime.datetime.utcnow() >= self._lastTime + self._duration:
                self._lastTime = datetime.datetime.utcnow()
                self._chat.send(self._message)
                if self._chat.isMod:
                    with getDatabase() as database:
                        timeout.recordTimeoutFromCommand(
                            database, self._chat, None, self._message, None,
                            'autorepeat')
                with self._countLock:
                    if self._count is not None:
                        self._count -= 1
            time.sleep(1/20)
        if ('repeatThread' in self._chat.sessionData
            and self._chat.sessionData['repeatThread'] is self):
            del self._chat.sessionData['repeatThread']
    
    def _continueRunning(self):
        with self._countLock:
            return self._count is None or self._count > 0
    
