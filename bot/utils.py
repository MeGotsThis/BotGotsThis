from . import data
from datetime import datetime
from types import TracebackType
from typing import Any, Iterable, List, Optional, Type, Tuple, Union  # noqa: F401,E501
import builtins
import bot
import bot.coroutine.logging
import os.path
import sys
import threading
import traceback

ExceptionInfo = Tuple[Optional[type], Optional[BaseException],
                      Optional[TracebackType]]


def now() -> datetime:
    return datetime.utcnow()


def joinChannel(broadcaster: str,
                priority: Union[int, float, str]=float('inf')
                ) -> bool:
    if not isinstance(broadcaster, str):
        raise TypeError()
    broadcaster = broadcaster.lower()
    if broadcaster in bot.globals.channels:
        t = min(bot.globals.channels[broadcaster].joinPriority, priority)
        bot.globals.channels[broadcaster].joinPriority = float(t)
        return False
    channel: data.Channel
    channel = data.Channel(broadcaster, bot.globals.cluster, priority)
    bot.globals.channels[broadcaster] = channel
    bot.globals.cluster.join_channel(channel)
    return True


def partChannel(channel: str) -> None:
    if not isinstance(channel, str):
        raise TypeError()
    if channel in bot.globals.channels:
        bot.globals.channels[channel].part()
        del bot.globals.channels[channel]


def whisper(nick: str, messages: Union[str, Iterable[str]]) -> None:
    bot.globals.cluster.messaging.sendWhisper(nick, messages)


def clearAllChat() -> None:
    bot.globals.cluster.messaging.clearAllChat()


def print(*args: Any,
          timestamp: Optional[datetime]=None,
          override: bool=False,
          file: Union[bool, str]=False) -> None:
    _timestamp: datetime = timestamp or now()
    if override or bot.config.development:
        builtins.print(_timestamp, *args)

    if file:
        filename: str
        if isinstance(file, str):
            filename = file
        else:
            filename = 'output.log'
        message: str = ' '.join(str(a) for a in args)
        bot.coroutine.logging.log(
            filename,
            f'{_timestamp:%Y-%m-%dT%H:%M:%S.%f} {message}\n')


def property_bool(value: Optional[bool]) -> Optional[str]:
    if value is None:
        return None
    return '1' if value else ''


def logIrcMessage(filename: str,
                  message: str,
                  timestamp: Optional[datetime]=None) -> None:
    if bot.config.ircLogFolder is None:
        return
    timestamp = timestamp or now()
    bot.coroutine.logging.log(
        os.path.join(bot.config.ircLogFolder, filename),
        f'{timestamp:%Y-%m-%dT%H:%M:%S.%f} {message}\n')


def logException(extraMessage: str='',
                 timestamp: Optional[datetime]=None) -> None:
    if bot.config.exceptionLog is None:
        return
    timestamp = timestamp or now()
    exceptType: Optional[Type[BaseException]]  # noqa: E701
    excecption: Optional[BaseException]
    trackback: Optional[TracebackType]
    excep: List[str]

    exceptType, excecption, trackback = sys.exc_info()
    excep = traceback.format_exception(exceptType, excecption, trackback)
    if extraMessage:
        extraMessage += '\n'
    threadName: str = threading.current_thread().name
    exception: str = ''.join(excep)  # noqa: E701
    bot.coroutine.logging.log(
        bot.config.exceptionLog, f'''\
{timestamp:%Y-%m-%dT%H:%M:%S.%f} Exception in thread {threadName}:
{extraMessage}{exception}''')
    if bot.config.development:
        builtins.print(
            timestamp,
            f'''\
Exception in thread {threadName}:
{extraMessage}{exception}''',
            file=sys.stderr)
