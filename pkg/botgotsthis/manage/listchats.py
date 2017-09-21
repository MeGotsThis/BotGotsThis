from typing import List  # noqa: F401

import bot
from lib.data import ManageBotArgs
from lib.helper import message


async def manageListChats(args: ManageBotArgs) -> bool:
    if bot.globals.channels:
        channels: List[str] = sorted(bot.globals.channels.keys())
        args.send(message.messagesFromItems(channels, 'Twitch Chats: '))
    else:
        args.send('I am somehow not in any channels, please help me here')
    return True
