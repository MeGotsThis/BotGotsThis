from bot import config, data, utils
from collections import defaultdict
from contextlib import suppress
from datetime import datetime, timedelta
from typing import Dict, Iterable, Iterator, Mapping, List, Optional, Tuple
from typing import Union
from ...database import DatabaseBase


def timeoutUser(database: DatabaseBase,
                chat: 'data.Channel',
                user: str,
                module: str,
                baseLevel: int=0,
                message: Optional[str]=None,
                reason: Optional[str]=None):
    properties = ['timeoutLength0', 'timeoutLength1', 'timeoutLength2']  # type: List[str]
    defaults = {'timeoutLength0': config.moderatorDefaultTimeout[0],
                'timeoutLength1': config.moderatorDefaultTimeout[1],
                'timeoutLength2': config.moderatorDefaultTimeout[2],
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
    duration = timedelta(seconds=config.warningDuration)  # type: timedelta
    if timestamp - chat.sessionData['timeouts'][module][user][0] >= duration:
        level = baseLevel  # type: int
    else:
        prevLevel = chat.sessionData['timeouts'][module][user][1]  # type: int
        level = min(max(baseLevel + 1, prevLevel + 1), 2)
    chat.sessionData['timeouts'][module][user] = timestamp, level
    length = timeouts[level]  # type: int
    if length:
        chat.send(
            '.timeout {user} {length}'.format(user=user, length=length), 0)
    else:
        chat.send('.ban {user}'.format(user=user), 0)
    database.recordTimeout(chat.channel, user, None, module, level, length,
                           message, reason)
    if reason is not None:
        lengthText = '{} seconds'.format(length) if length else 'Banned'
        utils.whisper(
            user,
            '{reason} ({length})'.format(reason=reason, length=lengthText))


def recordTimeoutFromCommand(database: DatabaseBase,
                             chat: 'data.Channel',
                             user: Optional[str],
                             messages: Union[str, Iterable[str], Iterator[str]],
                             sourceMessage: Optional[str],
                             module: str='custom'):
    if isinstance(messages, str):
        messages = messages,
    for message in messages:  # --type: str
        who, length = None, None  # type: Optional[str], Optional[int]
        if message.startswith(('.ban', '/ban')):
            with suppress(ValueError, IndexError):
                who, length = message.split()[1], 0
        if message.startswith(('.timeout', '/timeout')):
            with suppress(ValueError, IndexError):
                parts = message.split()
                who, length = parts[1], int(parts[2])
        if length is not None:
            database.recordTimeout(chat.channel, who, user, module, None,
                                   length, sourceMessage, None)
