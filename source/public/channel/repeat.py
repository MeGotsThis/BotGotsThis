import threading
import time
from bot import data, utils
from contextlib import suppress
from datetime import datetime, timedelta
from typing import Optional
from ..library import timeout
from ..library.chat import min_args, permission
from ...data import ChatCommandArgs
from ...database.factory import DatabaseBase, getDatabase


@permission('broadcaster')
def commandAutoRepeat(args: ChatCommandArgs) -> bool:
    """
    !autorepeat 1 MONEY MONEY
    !autorepeat 0
    !autorepeat off
    """
    
    count = None  # type: Optional[int]
    return processAutoRepeat(args, count)


@permission('broadcaster')
def commandAutoRepeatCount(args: ChatCommandArgs) -> bool:
    """
    !autorepeat-20 0.5 MONEY MONEY 
    !autorepeat-20 0
    !autorepeat-20 off
    """
    
    count = 10  # type: Optional[int]
    with suppress(ValueError, IndexError):
        count = int(args.message.command.split('autorepeat-')[1])
    return processAutoRepeat(args, count)


@min_args(2)
def processAutoRepeat(args: ChatCommandArgs,
                      count: Optional[int]) -> bool:
    if args.message.lower[1] == 'off':
        minutesDuration = 0  # type: float
    else:
        try:
            minutesDuration = float(args.message[1])
        except (ValueError):
            return False
    
    message = args.message[2:] or None  # type: Optional[str]
    if 'repeatThread' in args.chat.sessionData:
        args.chat.sessionData['repeatThread'].count = 0
    
    if minutesDuration <= 0 or count == 0 or not message:
        return True
    
    thread = MessageRepeater(
        chat=args.chat, message=message,
        duration=timedelta(minutes=minutesDuration), count=count)  # type: MessageRepeater
    args.chat.sessionData['repeatThread'] = thread
    thread.start()
    return True


class MessageRepeater(threading.Thread):
    def __init__(self, *args,
                 chat: 'data.Channel',
                 message: str='',
                 duration: timedelta=timedelta(),
                 count: Optional[int]=None,
                 **kwargs) -> None:
        threading.Thread.__init__(self, *args, **kwargs)
        self._chat = chat  # type: data.Channel
        self._message = message  # type: str
        self._count = count  # type: Optional[int]
        self._duration = max(duration, timedelta(seconds=1))  # type: timedelta
        self._lastTime = datetime.min  # type: datetime
        self._countLock = threading.Lock()  # type: threading.Lock
    
    @property
    def count(self) -> Optional[int]:
        with self._countLock:
            return self._count
    
    @count.setter
    def count(self, value: Optional[int]) -> None:
        with self._countLock:
            self._count = value
    
    def run(self) -> None:
        while self._continueRunning():
            self.process()
            time.sleep(1 / 20)
        if ('repeatThread' in self._chat.sessionData
                and self._chat.sessionData['repeatThread'] is self):
            del self._chat.sessionData['repeatThread']
    
    def process(self) -> None:
        now = utils.now()
        if now >= self._lastTime + self._duration:
            self._lastTime = now
            self._chat.send(self._message)
            if self._chat.isMod:
                with getDatabase() as database:  # --type: DatabaseBase
                    timeout.recordTimeoutFromCommand(
                        database, self._chat, None, self._message, None,
                        'autorepeat')
            with self._countLock:
                if self._count is not None:
                    self._count -= 1
    
    def _continueRunning(self):
        with self._countLock:
            return self._count is None or self._count > 0
