from ...data import ManageBotArgs, Send
from ...data.message import Message
from ...database import DatabaseBase
from lists.manage import methods


def manage_bot(database: DatabaseBase,
               send: Send,
               nick: str,
               message: Message) -> bool:
    argument = ManageBotArgs(database, send, nick, message)  # type: ManageBotArgs
    
    method = message.lower[1]  # type: str
    if method in methods and methods[method] is not None:
        return methods[method](argument)
    return False
