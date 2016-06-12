from bot import globals
from typing import List
from ..library.message import messagesFromItems
from ...data import ManageBotArgs


def manageListChats(args: ManageBotArgs) -> bool:
    if globals.channels:
        channels = sorted(globals.channels.keys())  # type: List[str]
        args.send(messagesFromItems(channels, 'Twitch Chats: '))
    else:
        args.send('I am somehow not in any channels, please help me here')
    return True
