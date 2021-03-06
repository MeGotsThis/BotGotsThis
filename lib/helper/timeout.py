import bot
from bot import data, utils  # noqa: F401
from collections import defaultdict
from contextlib import suppress
from datetime import datetime, timedelta
from typing import Dict, Iterable, Mapping, List, Optional, Union  # noqa: F401
from lib.cache import CacheStore
from lib.database import DatabaseTimeout


async def timeout_user(dataCache: CacheStore,
                       chat: 'data.Channel',
                       user: str,
                       module: str,
                       base_level: int=0,
                       message: Optional[str]=None,
                       reason: Optional[str]=None):
    properties: List[str]
    defaults: Dict[str, int]
    chatProp: Mapping[str, int]
    timeouts: List[int]
    properties = ['timeoutLength0', 'timeoutLength1', 'timeoutLength2']
    defaults = {'timeoutLength0': bot.config.moderatorDefaultTimeout[0],
                'timeoutLength1': bot.config.moderatorDefaultTimeout[1],
                'timeoutLength2': bot.config.moderatorDefaultTimeout[2],
                }
    chatProp = await dataCache.getChatProperties(chat.channel, properties,
                                                 defaults, int)
    timeouts = [chatProp['timeoutLength0'],
                chatProp['timeoutLength1'],
                chatProp['timeoutLength2'],
                ]

    if 'timeouts' not in chat.sessionData:
        chat.sessionData['timeouts'] = defaultdict(
            lambda: defaultdict(
                lambda: (datetime.min, 0)))

    timestamp: datetime = utils.now()
    duration: timedelta = timedelta(seconds=bot.config.warningDuration)
    level: int
    if timestamp - chat.sessionData['timeouts'][module][user][0] >= duration:
        level = min(max(base_level, 0), 2)
    else:
        prevLevel: int = chat.sessionData['timeouts'][module][user][1]
        level = min(max(base_level + 1, prevLevel + 1, 0), 2)
    chat.sessionData['timeouts'][module][user] = timestamp, level
    length: int = timeouts[level]
    theReason: str = reason or ''
    if length:
        chat.send(f'.timeout {user} {length} {theReason}', 0)
    else:
        chat.send(f'.ban {user} {theReason}', 0)

    db: DatabaseTimeout
    async with DatabaseTimeout.acquire() as db:
        await db.recordTimeout(chat.channel, user, None, module, level, length,
                               message, reason)


async def record_timeout(chat: 'data.Channel',
                         user: Optional[str],
                         messages: Union[str, Iterable[str]],
                         source_message: Optional[str],
                         module: str):
    if isinstance(messages, str):
        messages = messages,
    message: str
    for message in messages:
        who: Optional[str]
        length: Optional[Union[int, bool]]
        reason: Optional[str]
        parts: List[str]
        who, length = None, None
        reason = None
        if message.startswith(('.ban', '/ban')):
            parts = message.split(None, 2)
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
            db: DatabaseTimeout
            async with DatabaseTimeout.acquire() as db:
                await db.recordTimeout(chat.channel, who, user, module, None,
                                       length, source_message, reason)
