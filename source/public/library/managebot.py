import lists.manage
from ...data import ManageBotArgs, Send
from ...data.message import Message
from ...database import DatabaseBase


def manage_bot(database: DatabaseBase,
               send: Send,
               nick: str,
               message: Message) -> bool:
    argument = ManageBotArgs(database, send, nick, message)  # type: ManageBotArgs
    
    method = message.lower[1]  # type: str
    if (method in lists.manage.methods
            and lists.manage.methods[method] is not None):
        return lists.manage.methods[method](argument)
    return False
