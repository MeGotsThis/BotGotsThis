from bot import config, globals

def manageListChats(db, send, nick, message):
    prepend = 'Twitch Chats: '
    limit = config.messageLimit - len(prepend)
    channels = [c for c in globals.channels.keys()]
    channels.sort()
    chanList = []
    length = 0
    while channels:
        chan = channels.pop(0)
        chanList.append(chan)
        if length:
            length += 2
        length += len(chan)
        if length >= limit:
            if len(chanList) > 1:
                send(prepend + ', '.join(chanList[:-1]))
                del chanList[:-1]
                length = len(chan)
            else:
                send(prepend + ', '.join(chanList))
                chanList.clear()
                length = 0
    if chanList:
        send(prepend + ', '.join(chanList))
    return True
