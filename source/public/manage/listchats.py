import bot.globals
from typing import List
from ..library import message
from ...data import ManageBotArgs


def manageListChats(args: ManageBotArgs) -> bool:
    if bot.globals.channels:
        channels = sorted(bot.globals.channels.keys())  # type: List[str]
        args.send(message.messagesFromItems(channels, 'Twitch Chats: '))
    else:
        args.send('I am somehow not in any channels, please help me here')
    return True
