﻿import lists.manage
from typing import Mapping, Optional, Union  # noqa: F401
from ...data import ManageBotArgs, ManageBotCommand, Send  # noqa: F401
from ...data.message import Message
from ...data.permissions import ChatPermissionSet, WhisperPermissionSet
from ...database import DatabaseMain

Permissions = Union[WhisperPermissionSet, ChatPermissionSet]


async def manage_bot(database: DatabaseMain,
                     permissions: Permissions,
                     send: Send,
                     nick: str,
                     message: Message) -> bool:
    argument: ManageBotArgs
    argument = ManageBotArgs(database, permissions, send, nick, message)

    method: str = message.lower[1]
    methods: Mapping[str, Optional[ManageBotCommand]]
    methods = lists.manage.methods()
    if method in methods and methods[method] is not None:
        return await methods[method](argument)
    return False
