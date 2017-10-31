from typing import Mapping, Optional, Union  # noqa: F401

import lib.items.manage
from lib.data import ManageBotArgs, ManageBotCommand, Send  # noqa: F401
from lib.data.message import Message
from lib.data.permissions import ChatPermissionSet, WhisperPermissionSet
from lib.cache import CacheStore
from lib.database import DatabaseMain

Permissions = Union[WhisperPermissionSet, ChatPermissionSet]


async def manage_bot(data: CacheStore,
                     database: DatabaseMain,
                     permissions: Permissions,
                     send: Send,
                     nick: str,
                     message: Message) -> bool:
    argument: ManageBotArgs
    argument = ManageBotArgs(data, database, permissions, send, nick, message)

    method: str = message.lower[1]
    methods: Mapping[str, Optional[ManageBotCommand]]
    methods = lib.items.manage.methods()
    if method in methods and methods[method] is not None:
        return await methods[method](argument)
    return False
