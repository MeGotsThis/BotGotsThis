from bot import globals
from  ..library.message import messagesFromItems


def manageListChats(args):
    if globals.channels:
        channels = sorted(c for c in globals.channels.keys())
        args.send(messagesFromItems(channels, 'Twitch Chats: '))
    else:
        args.send('I am somehow not in any channels, please help me here')
    return True
