import lists.manage
from typing import Union
from ...data import ManageBotArgs, Send
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
    if (method in lists.manage.methods
            and lists.manage.methods[method] is not None):
        return await lists.manage.methods[method](argument)
    return False
