import bot.config
from bot import data, utils
from collections import defaultdict
from contextlib import suppress
from datetime import datetime, timedelta
from typing import Dict, Iterable, Iterator, Mapping, List, Optional, Tuple
from typing import Union
from ...database import DatabaseBase


def timeout_user(database: DatabaseBase,
                 chat: 'data.Channel',
                 user: str,
                 module: str,
                 base_level: int=0,
                 message: Optional[str]=None,
                 reason: Optional[str]=None):
    properties = ['timeoutLength0', 'timeoutLength1', 'timeoutLength2']  # type: List[str]
    defaults = {'timeoutLength0': bot.config.moderatorDefaultTimeout[0],
                'timeoutLength1': bot.config.moderatorDefaultTimeout[1],
                'timeoutLength2': bot.config.moderatorDefaultTimeout[2],
                }  # type: Dict[str, int]
    chatProp = database.getChatProperties(chat.channel, properties, defaults,
                                          int)  # type: Mapping[str, int]
    timeouts = (chatProp['timeoutLength0'],
                chatProp['timeoutLength1'],
                chatProp['timeoutLength2'],)  # type: Tuple[int, ...]
    
    if 'timeouts' not in chat.sessionData:
        chat.sessionData['timeouts'] = defaultdict(
            lambda: defaultdict(
                lambda: (datetime.min, 0)))
    
    timestamp = utils.now()  # type: datetime
    duration = timedelta(seconds=bot.config.warningDuration)  # type: timedelta
    if timestamp - chat.sessionData['timeouts'][module][user][0] >= duration:
        level = min(max(base_level, 0), 2)  # type: int
    else:
        prevLevel = chat.sessionData['timeouts'][module][user][1]  # type: int
        level = min(max(base_level + 1, prevLevel + 1, 0), 2)
    chat.sessionData['timeouts'][module][user] = timestamp, level
    length = timeouts[level]  # type: int
    if length:
        chat.send(
            '.timeout {user} {length} {reason}'.format(
                user=user, length=length, reason=reason or ''), 0)
    else:
        chat.send(
            '.ban {user} {reason}'.format(user=user, reason=reason or ''), 0)
    database.recordTimeout(chat.channel, user, None, module, level, length,
                           message, reason)


def record_timeout(database: DatabaseBase,
                   chat: 'data.Channel',
                   user: Optional[str],
                   messages: Union[str, Iterable[str]],
                   source_message: Optional[str],
                   module: str):
    if isinstance(messages, str):
        messages = messages,
    for message in messages:  # type: str
        who, length = None, None  # type: Optional[str], Optional[Union[int, bool]]
        reason = None  # type: Optional[str]
        if message.startswith(('.ban', '/ban')):
            parts = message.split(None, 2)  # type: List[str]
            if len(parts) >= 2:
                who, length = parts[1], 0
            if len(parts) >= 3:
                reason = parts[2]
        if message.startswith(('.timeout', '/timeout')):
            parts = message.split(None, 3)
            if len(parts) >= 2:
                if len(parts) < 3:
                    who = parts[1]
                else:
                    with suppress(ValueError):
                        who, length = parts[1], int(parts[2])
                    if len(parts) >= 4:
                        reason = parts[3]
        if who is not None:
            database.recordTimeout(chat.channel, who, user, module, None,
                                   length, source_message, reason)
