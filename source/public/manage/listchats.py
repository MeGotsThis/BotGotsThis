from bot import config, globals
from collections import deque

def manageListChats(args):
    prepend = 'Twitch Chats: '
    limit = config.args.messageLimit - len(prepend)
    channels = deque(sorted(c for c in globals.channels.keys()))
    chanList = []
    length = 0
    while channels:
        chan = channels.popleft()
        chanList.append(chan)
        if length:
            length += 2
        length += len(chan)
        if length >= limit:
            if len(chanList) > 1:
                args.send(prepend + ', '.join(chanList[:-1]))
                del chanList[:-1]
                length = len(chan)
            else:
                args.send(prepend + ', '.join(chanList))
                chanList.clear()
                length = 0
    if chanList:
        args.send(prepend + ', '.join(chanList))
    return True
