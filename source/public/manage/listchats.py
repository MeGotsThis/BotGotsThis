from  ..library.message import messagesFromItems
from bot import config, globals
from collections import deque

def manageListChats(args):
    if globals.channels:
        channels = sorted(c for c in globals.channels.keys())
        args.send(messagesFromItems(channels, 'Twitch Chats: '))
    else:
        args.send('I am somehow not in any channels, please help me here')
    return True
