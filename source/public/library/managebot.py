import lists.manage
from typing import Union
from ...data import ManageBotArgs, Send
from ...data.message import Message
from ...data.permissions import ChatPermissionSet, WhisperPermissionSet
from ...database import DatabaseBase


def manage_bot(database: DatabaseBase,
               permissions: Union[WhisperPermissionSet, ChatPermissionSet],
               send: Send,
               nick: str,
               message: Message) -> bool:
    argument = ManageBotArgs(database, permissions, send, nick, message)  # type: ManageBotArgs
    
    method = message.lower[1]  # type: str
    if (method in lists.manage.methods
            and lists.manage.methods[method] is not None):
        return lists.manage.methods[method](argument)
    return False
