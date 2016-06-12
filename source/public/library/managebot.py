from ...data import ManageBotArgs, Send
from ...data.message import Message
from ...database import DatabaseBase
from lists.manage import methods


def botManageBot(database: DatabaseBase,
                 send: Send,
                 nick: str,
                 message: Message) -> bool:
    argument = ManageBotArgs(database, send, nick, message)  # type: ManageBotArgs
    
    m = message.lower[1]  # type: str
    if m in methods and methods[m]:
        return methods[m](argument)
    return False
